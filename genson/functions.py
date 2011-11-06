import numpy as np
from util import resolve, genson_dumps, get_global_seed, assert_kwargs_consumed
from internal_ops import GenSONOperand

registry = {}


class GenSONFunction(GenSONOperand):
    def __init__(self, fun, name, args, kwargs):
        self.name = name
        self.fun = fun
        self.args = args
        self.kwargs = kwargs

    def __genson_eval__(self, context):
        resolved_args = []
        for a in self.args:
            resolved_args.append(resolve(a, context))

        resolved_kwargs = {}
        for k, v in self.kwargs.items():
            resolved_kwargs[k] = resolve(v, context)

        return self.fun(*resolved_args, **resolved_kwargs)

    def __genson_repr__(self, pretty_print=False, depth=0):
        arg_list = genson_dumps(self.args, pretty_print, 0)
        kwarg_list = ["%s=%s" % genson_dumps(x, pretty_print, depth)
                      for x in self.kwargs.items()]
        arg_str = ",".join(arg_list + tuple(kwarg_list))

        return "%s(%s)" % (self.name, arg_str)


def register_function(name, fun):
    def wrapper(*args, **kwargs):
        return GenSONFunction(fun, name, args, kwargs)
    registry[name] = wrapper

register_function('sin', np.sin)
register_function('cos', np.cos)
register_function('tan', np.tan)


class ParameterGenerator(GenSONOperand):

    def __init__(self, draws=1, random_seed=None):
        self.draws = draws
        self.counter = 0

        self.random_seed = random_seed
        self.seed()

    def reset(self):
        self.counter = 0
        self.seed()

    def seed(self, new_seed=None):
        if new_seed is not None:
            seed = self.random_seed = new_seed
        elif self.random_seed is None:
            seed = get_global_seed()
        else:
            seed = self.random_seed

        self.random = np.random.RandomState(seed=seed)

    def advance(self):
        self.counter += 1
        if self.counter >= self.draws:
            return False

        return True

    def __genson_eval__(self, context):
        raise NotImplementedError() 


class GridGenerator(ParameterGenerator):

    def __init__(self, *values, **kwargs):
        draws = kwargs.pop('draws', None)
        random_seed = kwargs.pop('random_seed', None)
        assert_kwargs_consumed(kwargs)

        ParameterGenerator.__init__(self, draws=draws, random_seed=random_seed)

        self.values = values
        if self.draws is None:
            self.draws = len(self.values)

        assert_kwargs_consumed(kwargs)

    def __genson_eval__(self, context):
        return self.values[self.counter]

    def __genson_repr__(self, pretty_print=False, depth=0):

        vals = [str(x) for x in genson_dumps(self.values)]
        val_str = ",".join(vals)
        if self.draws is not None:
            draws = ", draws=%s" % genson_dumps(self.draws)
        else:
            draws = ""
        return "<%s%s>" % (val_str, draws)

registry['grid'] = GridGenerator


def genson_call_str(name, *args, **kwargs):

    g_args = genson_dumps(args)
    g_kwargs = ["%s=%s" % genson_dumps(x)
                for x in kwargs.items() if x[1] is not None]

    return "%s(%s)" % (name, ",".join(g_args + tuple(g_kwargs)))


class GaussianRandomGenerator(ParameterGenerator):

    def __init__(self, mean, stdev, draws=1, random_seed=None, size=1):
        ParameterGenerator.__init__(self, draws=draws, random_seed=random_seed)
        self.mean = mean
        self.stdev = stdev
        self.size = size

    def __genson_eval__(self, context):
        size=resolve(self.size,context)
        if size != 1:
            return self.random.normal(resolve(self.mean, context),
                                  resolve(self.stdev, context),
                                  size=size)       
        else:
            return self.random.normal(resolve(self.mean, context),
                                      resolve(self.stdev, context))

    def __genson_repr__(self, pretty_print=False, depth=0):
        return genson_call_str('gaussian', self.mean, self.stdev,
                               draws=self.draws, random_seed=self.random_seed)
                               

registry['gaussian'] = GaussianRandomGenerator


class LognormalRandomGenerator(ParameterGenerator):

    def __init__(self, mean, stdev, draws=1, random_seed=None, size=1):
        ParameterGenerator.__init__(self, draws=draws, random_seed=random_seed)
        self.mean = mean
        self.stdev = stdev
        self.size = size

    def __genson_eval__(self, context):
        size=resolve(self.size,context)
        if size != 1:
            return self.random.lognormal(resolve(self.mean, context),
                                  resolve(self.stdev, context),
                                  size=size)       
        else:
            return self.random.lognormal(resolve(self.mean, context),
                                      resolve(self.stdev, context))

    def __genson_repr__(self, pretty_print=False,depth=0):
        return genson_call_str('lognormal', self.mean, self.stdev,
                               draws=self.draws, random_seed=self.random_seed)
                               

registry['lognormal'] = LognormalRandomGenerator


class QuantizedLognormalRandomGenerator(ParameterGenerator):

    def __init__(self, mean, stdev, round=1, draws=1, random_seed=None, size=1):
        ParameterGenerator.__init__(self, draws=draws, random_seed=random_seed)
        self.mean = mean
        self.stdev = stdev
        self.size = size
        self.round = round

    def __genson_eval__(self, context):
        size=resolve(self.size,context)
        if size != 1:
            val = self.random.lognormal(resolve(self.mean, context),
                                  resolve(self.stdev, context),
                                  size=size)       
        else:
            val = self.random.lognormal(resolve(self.mean, context),
                                      resolve(self.stdev, context))
                                      
        round = resolve(self.round,context)                             
        val = (np.ceil(val) // round).astype(np.int64) * round
        
        return val
        

    def __genson_repr__(self, pretty_print=False,depth=0):
        return genson_call_str('qlognormal', self.mean, self.stdev,
                               draws=self.draws, random_seed=self.random_seed)
                               

registry['qlognormal'] = QuantizedLognormalRandomGenerator



class UniformRandomGenerator(ParameterGenerator):

    def __init__(self, min, max, draws=1, random_seed=None, size=1):
        ParameterGenerator.__init__(self, draws=draws, random_seed=random_seed)
        self.min = min
        self.max = max
        self.size = size

    def __genson_eval__(self, context):
        size=resolve(self.size,context)
        if size != 1:
            return self.random.uniform(resolve(self.min, context),
                                   resolve(self.max, context),
                                   size=size)        
        else:
            return self.random.uniform(resolve(self.min, context),
                                       resolve(self.max, context))         


    def __genson_repr__(self, pretty_print=False, depth=0):
        return genson_call_str('uniform', self.min, self.max,
                               draws=self.draws, random_seed=self.random_seed)

registry['uniform'] = UniformRandomGenerator


class ChoiceRandomGenerator(ParameterGenerator):

    def __init__(self, vals, draws=1, random_seed=None, size=1):
        ParameterGenerator.__init__(self, draws=draws, random_seed=random_seed)
        self.vals = vals
        self.size = size

    def __genson_eval__(self, context):
        if self.size == 1:
            return self.vals[self.random.randint(len(self.vals))]
        else:
            return [self.vals[r] for r in self.random.randint(len(self.vals),size=self.size)]

    def __genson_repr__(self, pretty_print=False, depth=0):
        return genson_call_str('choice', *self.vals,
                               draws=self.draws, random_seed=self.random_seed)


registry['choice'] = ChoiceRandomGenerator


class RandintGenerator(ParameterGenerator):

    def __init__(self, min, max, draws=1, random_seed=None, size=1):
        ParameterGenerator.__init__(self, draws=draws, random_seed=random_seed)
        self.min = min
        self.max = max
        self.size = size
        self.vals = np.arange(min,max)
        

    def __genson_eval__(self, context):
        if self.size == 1:
            return self.vals[self.random.randint(len(self.vals))]
        else:
            return [self.vals[r] for r in self.random.randint(len(self.vals),size=self.size)]

    def __genson_repr__(self, pretty_print=False,depth=0):
        return genson_call_str('randint', *self.vals,
                               draws=self.draws, random_seed=self.random_seed)


registry['randint'] = RandintGenerator

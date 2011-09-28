import numpy as np
from util import resolve, genson_dumps
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
        arg_list = genson_dumps(self.args,pretty_print,0)
        kwarg_list = ["%s=%s" % genson_dumps(x,pretty_print,depth) 
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
    def __init__(self, draws=1, **kwargs):
        self.draws = draws
        self.counter = 0

    def reset(self):
        self.counter = 0

    def advance(self):
        self.counter += 1
        if self.counter >= self.draws:
            return False

        return True

    def __genson_eval__(self, context):
        raise NotImplementedError()


class GridGenerator(ParameterGenerator):

    def __init__(self, *values, **kwargs):
        draws = kwargs.get('draws', None)
        ParameterGenerator.__init__(self, draws, **kwargs)
        self.values = values
        if self.draws is None:
            self.draws = len(self.values)

    def __genson_eval__(self, context):
        return self.values[self.counter]
        
    def __genson_repr__(self,pretty_print=False,depth=0):
        
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

    def __init__(self, mean, stdev, draws=1, random_seed=None, **kwargs):
        ParameterGenerator.__init__(self, draws, **kwargs)
        self.mean = mean
        self.stdev = stdev
        self.random_seed = random_seed
        self.random = np.random.RandomState(seed=random_seed)

    def __genson_eval__(self, context):
        return self.random.normal(resolve(self.mean, context),
                                  resolve(self.stdev, context))
                                  
    def __genson_repr__(self, pretty_print=False,depth=0):
        return genson_call_str('gaussian', self.mean, self.stdev,
                               draws=self.draws, random_seed=self.random_seed)
        
        
registry['gaussian'] = GaussianRandomGenerator


class UniformRandomGenerator(ParameterGenerator):

    def __init__(self, min, max, draws=1, random_seed=None, **kwargs):
        ParameterGenerator.__init__(self, draws, **kwargs)
        self.min = min
        self.max = max
        self.random_seed = random_seed
        self.random = np.random.RandomState(seed=random_seed)

    def __genson_eval__(self, context):
        return self.random.uniform(resolve(self.min, context),
                                   resolve(self.max, context))

    def __genson_repr__(self, pretty_print=False,depth=0):
        return genson_call_str('uniform', self.min, self.max,
                               draws=self.draws, random_seed=self.random_seed)

registry['uniform'] = UniformRandomGenerator


class ChoiceRandomGenerator(ParameterGenerator):

    def __init__(self, vals, draws=1, random_seed=None, **kwargs):
        ParameterGenerator.__init__(self, draws, **kwargs)
        self.vals = vals
        self.random_seed = random_seed
        self.random = np.random.RandomState(seed=random_seed)

    def __genson_eval__(self, context):
        return self.vals[self.random.randint(len(self.vals))]

    def __genson_repr__(self, pretty_print=False,depth=0):
        return genson_call_str('choice', *self.vals,
                               draws=self.draws, random_seed=self.random_seed)
        
        
registry['choice'] = ChoiceRandomGenerator

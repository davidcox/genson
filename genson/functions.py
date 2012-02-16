import numpy as np
from util import resolve, genson_dumps, get_global_seed, assert_kwargs_consumed
from internal_ops import GenSONOperand
from internal_ops import GenSONFunction
from internal_ops import registry


def register_function(name, fun):
    if fun.__class__ is type and issubclass(fun, GenSONOperand):
        print('registering: %s' % name)
        f = fun
    else:
        def wrapper(*args, **kwargs):
            return GenSONFunction(fun, name, args, kwargs)

        f = wrapper

    # make the wrapper available to the parser
    registry[name] = f

    # make the wrapper available in this module
    current_module = __import__(__name__)
    setattr(current_module, name, f)

    return f

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
    """Return string representation of a GenSON function call
    """

    g_args = [genson_dumps(a) for a in args]
    g_kwargs = ["%s=%s" % (genson_dumps(k), genson_dumps(v))
                for k, v in kwargs.items() if v is not None]

    return "%s(%s)" % (name, ",".join(g_args + g_kwargs))


class GaussianRandomGenerator(ParameterGenerator):

    def __init__(self, mean, stdev, draws=1, random_seed=None, size=1):
        ParameterGenerator.__init__(self, draws=draws, random_seed=random_seed)
        self.mean = mean
        self.stdev = stdev
        self.size = size

    def __genson_eval__(self, context):
        size = resolve(self.size, context)
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
        size = resolve(self.size, context)
        if size != 1:
            return self.random.lognormal(resolve(self.mean, context),
                                         resolve(self.stdev, context),
                                         size=size)
        else:
            return self.random.lognormal(resolve(self.mean, context),
                                         resolve(self.stdev, context))

    def __genson_repr__(self, pretty_print=False, depth=0):
        return genson_call_str('lognormal', self.mean, self.stdev,
                               draws=self.draws, random_seed=self.random_seed)


register_function('lognormal', LognormalRandomGenerator)


class QuantizedLognormalRandomGenerator(ParameterGenerator):

    def __init__(self, mean, stdev, round=1, draws=1, random_seed=None,
                 size=1):
        ParameterGenerator.__init__(self, draws=draws, random_seed=random_seed)
        self.mean = mean
        self.stdev = stdev
        self.size = size
        self.round = round

    def __genson_eval__(self, context):
        size = resolve(self.size, context)
        if size != 1:
            val = self.random.lognormal(resolve(self.mean, context),
                                        resolve(self.stdev, context),
                                        size=size)
        else:
            val = self.random.lognormal(resolve(self.mean, context),
                                        resolve(self.stdev, context))

        round = resolve(self.round, context)
        val = (np.ceil(val) // round).astype(np.int64) * round

        return val

    def __genson_repr__(self, pretty_print=False, depth=0):
        return genson_call_str('qlognormal', self.mean, self.stdev,
                               draws=self.draws,
                               random_seed=self.random_seed)


register_function('qlognormal', QuantizedLognormalRandomGenerator)


class UniformRandomGenerator(ParameterGenerator):

    def __init__(self, min, max, draws=1, random_seed=None, size=1):
        ParameterGenerator.__init__(self, draws=draws, random_seed=random_seed)
        self.min = min
        self.max = max
        self.size = size

    def __genson_eval__(self, context):
        size = resolve(self.size, context)
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

register_function('uniform', UniformRandomGenerator)


class ChoiceRandomGenerator(ParameterGenerator):

    def __init__(self, vals, draws=1, random_seed=None, size=1):
        ParameterGenerator.__init__(self, draws=draws, random_seed=random_seed)
        self.vals = vals
        self.size = size

    def __genson_eval__(self, context):
        if self.size == 1:
            return self.vals[self.random.randint(len(self.vals))]
        else:
            return [self.vals[r] for r in
                    self.random.randint(len(self.vals), size=self.size)]

    def __genson_repr__(self, pretty_print=False, depth=0):
        return genson_call_str('choice', *self.vals,
                               draws=self.draws, random_seed=self.random_seed)


register_function('choice', ChoiceRandomGenerator)


class RandintGenerator(ParameterGenerator):

    def __init__(self, min, max, draws=1, random_seed=None, size=1):
        ParameterGenerator.__init__(self, draws=draws, random_seed=random_seed)
        self.min = min
        self.max = max
        self.size = size
        self.vals = np.arange(min, max)

    def __genson_eval__(self, context):
        if self.size == 1:
            return self.vals[self.random.randint(len(self.vals))]
        else:
            return [self.vals[r] for r in
                    self.random.randint(len(self.vals), size=self.size)]

    def __genson_repr__(self, pretty_print=False, depth=0):
        return genson_call_str('randint', *self.vals,
                               draws=self.draws, random_seed=self.random_seed)


register_function('randint', RandintGenerator)

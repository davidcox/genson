import numpy
import numpy.random
from util import *
from internal_ops import *

registry = {}

class GenSONFunction (GenSONOperand):
    def __init__(self, fun, args, kwargs):
        self.fun = fun
        self.args = args
        self.kwargs = kwargs
    
    def __genson_eval__(self, context):
        resolved_args = []
        for a in self.args:
            resolved_args.append(resolve(a,context))
        
        resolved_kwargs = {}
        for (k,v) in self.kwargs.items():
            resolved_kwargs[k] = resolve(v,context)
        
        return self.fun(*resolved_args, **resolved_kwargs)

def register_function(name, fun):
    def wrapper(*args, **kwargs):
        return GenSONFunction(fun, args, kwargs)
    registry[name] = wrapper

register_function('sin', numpy.sin)
register_function('cos', numpy.cos)
register_function('tan', numpy.tan)

class ParameterGenerator (GenSONOperand):
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

        
class GridGenerator (ParameterGenerator):

    def __init__(self, *values, **kwargs):
        draws = kwargs.get('draws',None)
        ParameterGenerator.__init__(self,draws,**kwargs)
        self.values = values
        if self.draws is None:
            self.draws = len(self.values)
        
    def __genson_eval__(self, context):
        return self.values[self.counter]

registry['grid'] = GridGenerator


class GaussianRandomGenerator (ParameterGenerator):
    
    def __init__(self, mean, stdev, draws=1, **kwargs):
        ParameterGenerator.__init__(self, draws,**kwargs)
        self.mean = mean
        self.stdev = stdev

    def __genson_eval__(self, context):
        return numpy.random.normal(resolve(self.mean, context), 
                                   resolve(self.stdev, context))
    
registry['gaussian'] = GaussianRandomGenerator


class UniformRandomGenerator (ParameterGenerator):
    
    def __init__(self, min, max, draws=1, **kwargs):
        ParameterGenerator.__init__(self, draws, **kwargs)
        self.min = min
        self.max = max

    def __genson_eval__(self, context):
        return numpy.random.uniform(resolve(self.min, context),
                                    resolve(self.max))
    
registry['uniform'] = UniformRandomGenerator





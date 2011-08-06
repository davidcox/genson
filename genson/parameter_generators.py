import numpy.random

generators = {}


class ParameterGenerator:
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

    def value(self):
        raise NotImplementedError()

        
class GridGenerator (ParameterGenerator):

    def __init__(self, *values, **kwargs):
        draws = kwargs.get('draws',None)
        ParameterGenerator.__init__(self,draws,**kwargs)
        self.values = values
        if self.draws is None:
            self.draws = len(self.values)
        
    def value(self):
        return self.values[self.counter]

generators['grid'] = GridGenerator


class GaussianRandomGenerator (ParameterGenerator):
    
    def __init__(self, mean, stdev, draws=1, **kwargs):
        ParameterGenerator.__init__(self, draws,**kwargs)
        self.mean = mean
        self.stdev = stdev

    def value(self):
        return numpy.random.normal(self.mean, self.stdev)
    
generators['gaussian'] = GaussianRandomGenerator


class UniformRandomGenerator (ParameterGenerator):
    
    def __init__(self, min, max, draws=1, **kwargs):
        ParameterGenerator.__init__(self, draws, **kwargs)
        self.min = min
        self.max = max

    def value(self):
        return numpy.random.uniform(self.min, self.max)
    
generators['uniform'] = UniformRandomGenerator





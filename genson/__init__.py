from parser import *
from functions import *
from util import *
import copy

class JSONGenerator:

    def __init__(self, genson_dict):
        self.genson_dict = genson_dict

        self.generators = []
        self.find_generators(genson_dict)

        self.first_run = True

    def find_generators(self, d):
        vals = d.values()
        for v in vals:
            if isinstance(v, ParameterGenerator):
                self.generators.append(v)
            if isdict(v):
                self.find_generators(v)

    def __iter__(self):
        return self


    def advance_generator_stack(self, cursor=0):

        if cursor >= len(self.generators):
            return False

        if self.generators[cursor].advance():
            return True
        else:
            self.generators[cursor].reset()
            return self.advance_generator_stack(cursor+1)


    def next(self):

        if self.first_run:
            self.first_run = False
            return resolve(self.genson_dict)

        if self.advance_generator_stack():
            return resolve(self.genson_dict)
        else:
            self.first_run = True
            raise StopIteration()


def load(io):
    s = "\n".join(io.readlines())
    return loads(s)

def loads(genson_string):
    parser = GENSONParser()
    genson_dict = parser.parse_string(genson_string)
    return JSONGenerator(genson_dict)

def dumps(generator, prettyprint=False):
    if isdict(generator):
        return genson_dumps(generator, prettyprint)
    else:
        return genson_dumps(generator.genson_dict, prettyprint)
from parser import *
from functions import *
from util import *


class JSONGenerator:
    def __init__(self, genson_dict):
        self.genson_dict = genson_dict

        self.generators = []
        self.find_generators(genson_dict)

        self.first_run = True

    def find_generators(self, d):
        if isdict(d):
            vals = d.values()
        elif isiterable(d):
            vals = d

        for v in vals:
            if isinstance(v, ParameterGenerator):
                self.generators.append(v)
            if isdict(v) or isiterable(v):
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
            return self.advance_generator_stack(cursor + 1)

    def next(self):

        if self.first_run:
            self.first_run = False
            return resolve(self.genson_dict)

        if self.advance_generator_stack():
            return resolve(self.genson_dict)
        else:
            self.first_run = True
            raise StopIteration()

    def reset(self):
        for g in self.generators:
            g.reset()

    # dictionary support
    def __getitem__(self, key):
        return self.genson_dict[key]

    def keys(self):
        return self.genson_dict.keys()


def load(io):
    s = "\n".join(io.readlines())
    return loads(s)


def loads(genson_string):
    parser = GENSONParser()
    genson_dict = parser.parse_string(genson_string)
    return JSONGenerator(genson_dict)


def dumps(generator, pretty_print=False):
    if isdict(generator):
        return genson_dumps(generator, pretty_print)
    else:
        return genson_dumps(generator.genson_dict, pretty_print)

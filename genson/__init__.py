from parser import GENSONParser
from internal_ops import GenSONFunction
from internal_ops import GenSONOperand
from internal_ops import lazy
from internal_ops import lazyinfo
from internal_ops import LazyCall
from internal_ops import literal
from internal_ops import register_lazy
from references import ref
import functions
from functions import ParameterGenerator
from util import *
import copy
from collections import OrderedDict


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
        else:
            raise TypeError('invalid generator document', d)

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

        d = copy.deepcopy(self.genson_dict)

        if self.first_run:
            self.first_run = False
            return resolve(d)

        if self.advance_generator_stack():
            return resolve(d)
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
    elif hasattr(generator, 'genson_dict'):
        return genson_dumps(generator.genson_dict, pretty_print)

    else:
        return genson_dumps(generator, pretty_print)


# Currently not used
def node_eval(obj, memo):

    # -- dictionary containers
    if isinstance(obj, (dict, OrderedDict)):
        # XXX: this will evaluate in undefined order for dicts
        waiting_on = [v for v in obj.values() if id(v) not in memo]
        if not waiting_on:
            memo[id(obj)] = dict([(k, memo[id(v)]) for k, v in obj.items()])

    # -- callable nodes
    elif isinstance(obj, GenSONFunction):
        # XXX: this will evaluate in undefined order for kwargs
        inputs = list(obj.args) + obj.kwargs.values()
        waiting_on = [v for v in inputs if id(v) not in memo]
        if not waiting_on:
            args = [memo[id(v)] for v in obj.args]
            kwargs = dict([(k, memo[id(v)]) for k, v in obj.kwargs.items()])
            memo[id(obj)] = obj.fun(*args, **kwargs)

    # -- iterable containers
    elif isinstance(obj, (list, tuple)):
        waiting_on = [v for v in obj if id(v) not in memo]
        if not waiting_on:
            memo[id(obj)] = type(obj)([memo[id(v)] for v in obj])

    # -- types that pass-through
    elif isinstance(obj, (int, float, str, np.ndarray)):
        waiting_on = []
        memo[id(obj)] = obj

    # -- literals that pass-through
    elif obj in (None,):
        waiting_on = []
        memo[id(obj)] = obj

    # -- anything else
    else:
        raise NotImplementedError(obj)

    if waiting_on:
        return [obj] + waiting_on
    else:
        return waiting_on


STACK_LIMIT = 10000


# Currently not used
def rec_eval(todo, memo):
    """
    Returns nodes required by this one.
    Updates the memo by side effect. Returning [] means this node has been
    computed and the value is available as memo[id(node)]
    """
    while todo:
        if len(todo) > STACK_LIMIT:
            raise RuntimeError('Probably infinite loop in document')
        node = todo.pop()
        if id(node) not in memo:
            todo.extend(node_eval(node, memo))

ARGS_KEY = '__args__'
KWARGS_KEY = '__kwargs__'
ARGS_REF = 'root.%s' % ARGS_KEY
KWARGS_REF = 'root.%s' % KWARGS_KEY


class JSONFunction(object):

    ARGS = ref('root.__args__')
    KWARGS = ref('root.__kwargs__')

    def __init__(self, prog_son):
        self.prog_son = prog_son

    def __call__(self, *_args, **_kwargs):
        prog = copy.deepcopy(self.prog_son)
        prog['__args__'] = copy.deepcopy(_args)
        prog['__kwargs__'] = copy.deepcopy(_kwargs)

        rval = resolve(prog)
        rval.pop('__args__')
        rval.pop('__kwargs__')
        return rval


# Currently not used
class JAMES_JSONFunction(object):
    """Make a GenSON document into a callable function
    """
    # TODO: make the treatment of args and kwargs in the document
    #       more Python-like. The current implementation requires that
    #       parameters (and hence arguments as well) be divided between
    #       positional and keyword, which python does not require.

    # -- This construction allow ARGS and KWARGS to be lazily-indexed
    _ARGS = []
    _KWARGS = {}
    ARGS = internal_ops.identity.lazy(_ARGS)
    KWARGS = internal_ops.identity.lazy(_KWARGS)

    def __init__(self, prog):
        self.prog = prog

    def __call__(self, *args, **kwargs):
        prog, ARGS, KWARGS = copy.deepcopy(
                (self.prog, self._ARGS, self._KWARGS))
        ARGS[:] = [literal(a) for a in args]
        KWARGS.update(dict([(k, literal(v)) for k, v in kwargs.items()]))

        memo = {}
        rec_eval([prog], memo)
        rval = memo[id(prog)]
        return rval

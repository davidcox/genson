from util import resolve, genson_dumps


class GenSONBinaryOp:
    def __init__(self,a,b,op):
        self.a = a
        self.b = b
        self.op = op

    def __genson_eval__(self, context):

        res_a = resolve(self.a, context)
        res_b = resolve(self.b, context)

        if self.op is '+':
            return res_a + res_b
        elif self.op is '-':
            return res_a - res_b
        elif self.op is '*':
            return res_a * res_b
        elif self.op is '/':
            return res_a / res_b
        elif self.op is '**':
            return res_a / res_b

    def __genson_repr__(self, pretty_print=False, depth=0):
        return "%s %s %s" % (genson_dumps(self.a),
                             self.op,
                             genson_dumps(self.b))


class GenSONUnaryOp:
    def __init__(self, a, op):
        self.a = a
        self.op = op

    def __genson_eval__(self, context):

        res_a = resolve(self.a, context)
        if self.op is '+':
            return res_a
        if self.op is '-':
            return -res_a

    def __genson_repr__(self, pretty_print=False, depth=0):
        return "%s %s" % (self.op, genson_dumps(self.a))


class GenSONOperand(object):
    def __add__(self, other):
        return GenSONBinaryOp(self, other, '+')
    def __radd__(self, other):
        return GenSONBinaryOp(other, self, '+')
    def __sub__(self, other):
        return GenSONBinaryOp(self, other, '-')
    def __rsub__(self, other):
        return GenSONBinaryOp(other, self, '-')
    def __mul__(self, other):
        return GenSONBinaryOp(self, other, '*')
    def __rmul__(self, other):
        return GenSONBinaryOp(other, self, '*')
    def __div__(self, other):
        return GenSONBinaryOp(self, other, '/')
    def __rdiv__(self, other):
        return GenSONBinaryOp(other, self, '/')
    def __pow__(self, other):
        return GenSONBinaryOp(self, other, '**')
    def __rpow__(self, other):
        return GenSONBinaryOp(other, self, '**')
    def __neg__(self, other):
        return GenSONUnaryOp(self, '-')
    def __pos__(self, other):
        return GenSONUnaryOp(self, '+')
    def __getitem__(self, idx):
        # XXX: add unit test of argument unpacking
        try:
            ll = len(self)
        except:
            ll = None
        if isinstance(idx, int):
            if ll is not None and idx >= ll:
                #  -- this IndexError is essential for supporting
                #     tuple-unpacking syntax or list coersion of self.
                raise IndexError(idx)
        return GenSONFunction(
                lambda thing, idx: thing[idx],
                'getitem',
                (self, idx),
                {})
    def set_info(self, info):
        self._info = info
    def __len__(self):
        try:
            return self._info['len']
        except (AttributeError, KeyError):
            return object.__len__(self)


# Expedient trickiness
def quicky_populate(cls, method_list):
    for m in method_list:
        source = GenSONOperand.__dict__[m]
        cls.__dict__[m] = source

op_list = [  '__add__', '__radd__',
             '__sub__', '__rsub__',
             '__mul__', '__rmul__',
             '__div__', '__rdiv__',
             '__pos__', '__neg__',
             '__pow__', '__rpow__']

quicky_populate(GenSONBinaryOp, op_list)
quicky_populate(GenSONUnaryOp, op_list)

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
        """
            name(
                    arg1,
                    arg2,
                kw1=
                    arg3,
                kw2=
                    arg4
            )
        """
        lines = [self.name + '(']
        for a in self.args:
            lines.append('%s%s,' % (
                '\t' * (depth + 2),
                genson_dumps(a, pretty_print, depth + 2)))
        for k, v in self.kwargs.iteritems():
            lines.append('\t' * (depth + 1) + k + '=')
            lines.append('%s%s,' % (
                '\t' * (depth + 2),
                genson_dumps(v, pretty_print, depth + 2)))
        lines.append('\t' * depth + ')')
        return '\n'.join(lines)


def register_function(name, fun):
    def wrapper(*args, **kwargs):
        return GenSONFunction(fun, name, args, kwargs)
    registry[name] = wrapper


class LazyCall(object):
    """
    Class for decorating functions and making them GenSON-compatible.

    Usage:

    >>> @register_lazy
    >>> def f(a, b=True):
    >>>     return a if b else None
    >>> f(1)              # returns 1
    >>> f(1, False)       # returns None
    >>> f.lazy(1, False)  # saves args, kwargs, returns a GenSONFunction


    """
    info = None
    def __init__(self, fn, registry_name=None):
        self.fn = fn
        if registry_name:
            registry[registry_name] = self.lazy

    def __call__(self, *args, **kwargs):
        return self.fn(*args, **kwargs)

    def lazy(self, *args, **kwargs):
        rval = GenSONFunction(
                self.fn,
                self.fn.__name__,
                args,
                kwargs)
        if self.info:
            rval.set_info(self.info)
        return rval

def lazy(f):
    return LazyCall(f)

def register_lazy(f):
    return LazyCall(f, registry_name=f.__name__)

def lazyinfo(**info):
    def deco(f):
        rval = LazyCall(f, registry_name=f.__name__)
        rval.info = info
        return rval
    return deco

@lazy
def identity(obj):
    return obj

def literal(obj):
    return LazyCall(lambda : obj, registry_name=None).lazy()

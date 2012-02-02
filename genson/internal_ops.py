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


class GenSONOperand:
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


# Expedient trickiness
def quicky_populate(cls, method_list):
    for m in method_list:
        source = GenSONOperand.__dict__[m]
        cls.__dict__[m] = source

op_list = ['__add__', '__radd__',
           '__sub__', '__rsub__',
           '__mul__', '__rmul__',
           '__div__', '__rdiv__',
           '__pos__', '__neg__',
           '__pow__', '__rpow__']

quicky_populate(GenSONBinaryOp, op_list)
quicky_populate(GenSONUnaryOp, op_list)

from collections import OrderedDict
from genson import lazy
from genson import JSONFunction
from genson import ref
import genson


@lazy
def foo(a, b=None):
    return 'first_arg', 'second_arg', a, b


def test_lazy_callable():
    assert foo(1) == ('first_arg', 'second_arg', 1, None)
    assert foo(1, 3) == ('first_arg', 'second_arg', 1, 3)
    assert foo(1, b=3) == ('first_arg', 'second_arg', 1, 3)
    assert foo(b=3, a=1) == ('first_arg', 'second_arg', 1, 3)


def test_lazy_getitem_args_kwargs():
    # -- construct a program document directly
    #    without passing through the parser
    prog = OrderedDict()
    prog['test0'] = 4
    prog['test1'] = foo.lazy(1)
    prog['test4'] = JSONFunction.ARGS[0]
    prog['test5'] = JSONFunction.KWARGS['aaa']

    wanted = dict(
            test0=4,
            test1=('first_arg', 'second_arg', 1, None),
            test4=33,
            test5='hello')

    print genson.dumps(prog, pretty_print=True)

    f = JSONFunction(prog)
    result = dict(f(33, aaa='hello'))
    assert result == wanted


def test_ref():
    # XXX This fails because ref's aren't yet implemented with JSONFunction
    # and rec_eval
    prog = OrderedDict()
    prog['a'] = 5
    prog['result'] = foo.lazy(ref('a'))
    f = JSONFunction(prog)
    assert f()['result'] == 5


def test_ref_within_lazy_function_root():
    prog = OrderedDict()
    prog['a'] = 5
    prog['result'] = foo.lazy(ref('root.a'))
    f = JSONFunction(prog)
    print f()['result']
    assert f()['result'] == 5

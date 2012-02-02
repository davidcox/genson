from collections import OrderedDict
from genson import lazy
from genson import JSONFunction
from genson import ref
from genson import FROM_KWARGS
from genson import FROM_ARGS


@lazy
def foo(a, b=None):
    return 'first_arg', 'second_arg', a, b

def test_lazy_callable():
    assert foo(1) == ('first_arg', 'second_arg', 1, None)
    assert foo(1, 3) == ('first_arg', 'second_arg', 1, 3)
    assert foo(1, b=3) == ('first_arg', 'second_arg', 1, 3)
    assert foo(b=3, a=1) == ('first_arg', 'second_arg', 1, 3)

def test_lazy_getitem_calldoc_args_kwargs():
    # -- construct a program document directly
    #    without passing through the parser
    prog = OrderedDict()
    prog['args'] = FROM_ARGS
    prog['kwargs'] = FROM_KWARGS
    prog['test0'] = 4
    prog['test1'] = foo.lazy(1)
    prog['test2'] = ref('test1')[0]
    prog['test3'] = ref('test1')[1]
    prog['test4'] = ref('args')[0]
    prog['test5'] = ref('kwargs')['aaa']

    wanted = dict(
            test0=4,
            test1=('first_arg', 'second_arg', 1, None),
            test2='first_arg',
            test3='second_arg',
            test4=33,
            test5='hello')

    print prog
    f = JSONFunction(prog)
    result = dict(f(33, aaa='hello'))
    print result
    assert result == wanted

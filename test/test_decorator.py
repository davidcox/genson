
from genson import register_lazy, JSONGenerator
from genson.references import ref


def test_genson_function_decorator():

    @register_lazy
    def double_it(x):
        return 2 * x

    g = JSONGenerator({'a': 4, 'b': double_it(ref('this.a'))})

    d = g.next()

    assert(d['a'] == 4)
    assert(d['b'] == 8)

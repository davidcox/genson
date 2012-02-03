import genson
from genson import ref


def test_array_references():
    g = genson.loads('{"a":[uniform(0,1),1,2], "b": this.a.1 }')
    d = g.next()
    assert(d['a'][1] == d['b'])


def test_parent_reference():
    s = """
        {
         "a": 1,
         "b": { "c": 2 * parent.a }
        }

    """

    g = genson.loads(s)
    d = g.next()
    assert(d['b']['c'] == 2 * d['a'])


def test_nested_parent_reference():
    s = """
        {
         "a": 1,
         "b": {
                "c": {
                        "d": 2 * parent.parent.a
                     }
              }
        }

    """

    g = genson.loads(s)
    d = g.next()
    assert(d['b']['c']['d'] == 2 * d['a'])


def test_lookahead_reference():
    s = """
        {
         "b": { "c": 2 * parent.a },
         "a": 1
        }

    """

    g = genson.loads(s)
    d = g.next()
    assert(d['b']['c'] == 2 * d['a'])


def test_root_reference():
    s = """
        {
         "b": { "c": 2 * root.a },
         "a": 1
        }

    """

    g = genson.loads(s)
    d = g.next()
    assert(d['b']['c'] == 2 * d['a'])


def test_up_one_leg_down_another():
    d = {'a': {'b': 5}, 'c': {'d': {'e': ref('parent.parent.a.b')}}}

    g = genson.JSONGenerator(d)

    r = g.next()
    assert(r['a']['b'] == r['c']['d']['e'])

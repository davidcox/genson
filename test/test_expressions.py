import genson


def test_unary():

    g = genson.loads('{ "p" : sin(-1) } ')
    assert(g['p'].args[0] == -1)

    g = genson.loads('{ "p" : sin(+1) } ')
    assert(g['p'].args[0] == 1)


def test_binary():

    g = genson.loads('{ "p" : gaussian(1+1,1) } ')
    assert(g['p'].mean == 2)
    assert(g['p'].stdev == 1)

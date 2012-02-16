from genson.functions import GridGenerator


def test_extra_kwargs():

    raised = False
    try:
        g = GridGenerator(1, 2, 3, spurious_kwarg=4)
    except ValueError:
        raised = True

    assert(raised == True)

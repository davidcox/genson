from genson import GridGenerator


def test_extra_kwargs():
    
    raised = False
    try:
        g = GridGenerator(1,2,3, spurious_kwarg=4)
    except ValueError as e:
        raised = True
    
    assert(raised == True)
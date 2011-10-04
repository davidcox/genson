import genson

def test_multi_gen_kwargs():
    gson = \
    """
    {
        "multi_gen_kwargs_bug" : { "nested": gaussian(0, 1, draws=1, random_seed=42) }
    }
    """
    genson.loads(gson)


def test_gen_kwargs_with_underscore():
    gson = \
    """
    {
        "gen_kwarg_with_underscore" : { "nested": gaussian(0, 1, draws=1, random_seed=42) }
    }
    """
    genson.loads(gson)


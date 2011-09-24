from nose.tools import assert_equal

import genson

def test_gaussian_random_seed():
    gson = \
    """
    {
        "gaussian_random_seed" : gaussian(0, 1, draws=1, random_seed=42)
    }
    """
    val = genson.loads(gson).next()['gaussian_random_seed']
    assert_equal(val, 0.4967141530112327)


def test_gaussian_uniform_seed():
    gson = \
    """
    {
        "gaussian_uniform_seed" : uniform(0, 1, draws=1, random_seed=42)
    }
    """
    val = genson.loads(gson).next()['gaussian_uniform_seed']
    assert_equal(val, 0.3745401188473625)

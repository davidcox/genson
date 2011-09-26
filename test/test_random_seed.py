from nose.tools import assert_equal

import genson

def test_gaussian_random_seed():
    gson = \
    """
    {
        "gaussian_random_seed" : gaussian(0, 1, draws=2, random_seed=42)
    }
    """
    vals = [val['gaussian_random_seed'] for val in genson.loads(gson)]
    assert_equal(vals[0], 0.4967141530112327)
    assert_equal(vals[1], -0.13826430117118466)


def test_gaussian_uniform_seed():
    gson = \
    """
    {
        "uniform_random_seed" : uniform(0, 1, draws=2, random_seed=42)
    }
    """
    vals = [val['uniform_random_seed'] for val in genson.loads(gson)]
    assert_equal(vals[0], 0.3745401188473625)
    assert_equal(vals[1], 0.9507143064099162)

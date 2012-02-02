from nose.tools import assert_equal, assert_not_equal
from nose import with_setup

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


def test_gaussian_random_seed_multi_call():
    gson = '{"param0": gaussian(0, 1, draws=10, random_seed=42)}'
    r1 = [e for e in genson.loads(gson)]
    r2 = [e for e in genson.loads(gson)]
    assert_equal(r1, r2)


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


def setup_global_seed():
    genson.set_global_seed(None)


def teardown_global_seed():
    genson.set_global_seed(None)


@with_setup(setup_global_seed, teardown_global_seed)
def test_gaussian_random_seed2():

    genson.set_global_seed(42)

    gson = \
    """
    {
        "gaussian_random_seed" : gaussian(0, 1, draws=2)
    }
    """
    gen = genson.loads(gson)
    vals = [val['gaussian_random_seed'] for val in gen]
    assert_equal(vals[0], 0.4967141530112327)
    assert_equal(vals[1], -0.13826430117118466)

    genson.set_global_seed(None)
    gen.reset()
    vals = [val['gaussian_random_seed'] for val in gen]
    assert_not_equal(vals[0], 0.4967141530112327)
    assert_not_equal(vals[1], -0.13826430117118466)

    genson.set_global_seed(42)
    gen.reset()
    gen = genson.loads(gson)
    vals = [val['gaussian_random_seed'] for val in gen]
    assert_equal(vals[0], 0.4967141530112327)
    assert_equal(vals[1], -0.13826430117118466)



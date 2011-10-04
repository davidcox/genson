from nose.tools import assert_equals
import genson

specs = [
    ("""
    {
        "a": choice([1, 2, 3], draws=1000, random_seed=42),
        "b": choice([4, 5, 6], draws=1000, random_seed=42)
    }
    """,
     [{'a': 3, 'b': 6}, {'a': 1, 'b': 4}, {'a': 3, 'b': 6},
      {'a': 3, 'b': 6}, {'a': 1, 'b': 4}]
    ),

    ("""
    {
        "a": [choice([1, 2, 3], draws=1000, random_seed=42),
              choice([4, 5, 6], draws=1000, random_seed=42)]
    }
    """,
     [{'a': [3, 6]}, {'a': [1, 4]}, {'a': [3, 6]},
      {'a': [3, 6]}, {'a': [1, 4]}]
    ),

    ("""
    {
        "a":
        {
        "b": grid(1, 2),
        "c": choice([6, 7, 8], draws=1000, random_seed=42)
        }
    }
    """,
     [{'a': {'c': 8, 'b': 1}}, {'a': {'c': 6, 'b': 2}},
      {'a': {'c': 8, 'b': 1}}, {'a': {'c': 8, 'b': 2}},
      {'a': {'c': 6, 'b': 1}}]
    ),

    ("""
    {
        "a":
        [
        {
            "b": choice([1, 2, 3, 4], draws=1000, random_seed=42),
            "c": choice([5, 6], draws=1000, random_seed=42)
        }
        ]
    }
    """,
     [{'a': [{'c': 5, 'b': 3}]}, {'a': [{'c': 6, 'b': 4}]},
      {'a': [{'c': 5, 'b': 1}]}, {'a': [{'c': 5, 'b': 3}]},
      {'a': [{'c': 5, 'b': 3}]}]
    ),
    ]


def test_gens_in_lists():

    for spec, gt in specs:
        it = genson.loads(spec)
        gv = [it.next() for _ in xrange(5)]
        yield assert_equals, gv, gt

from nose.tools import assert_equals
import genson

specs = [
    ("""
     [
     choice([1, 2, 3], draws=1000, random_seed=42),
     choice([4, 5, 6], draws=1000, random_seed=42)
    ]
    """,
     [[3, 6], [1, 4], [3, 6], [3, 6], [1, 4]]
    ),

    ("""
    (
        choice([1, 2, 3], draws=1000, random_seed=42),
        choice([4, 5, 6], draws=1000, random_seed=42)
    )
    """,
     [(3, 6), (1, 4), (3, 6), (3, 6), (1, 4)]
    ),

    ("""
    [
        [
            choice([1, 2, 3], draws=1000, random_seed=42),
            choice([4, 5, 6], draws=1000, random_seed=42)
        ]
    ]
    """,
     [[[3, 6]], [[1, 4]], [[3, 6]], [[3, 6]], [[1, 4]]]
    ),

    ("""
    [
        {
        "b": grid(1, 2),
        "c": choice([6, 7, 8], draws=1000, random_seed=42)
        }
    ]
    """,
     [[{'c': 8, 'b': 1}], [{'c': 6, 'b': 2}], [{'c': 8, 'b': 1}],
      [{'c': 8, 'b': 2}], [{'c': 6, 'b': 1}]]
    ),
]


def test_outermost_lists():

    for spec, gt in specs:
        it = genson.loads(spec)
        gv = [it.next() for _ in xrange(5)]
        yield assert_equals, gv, gt

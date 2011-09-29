import genson

specs = [
"""
[
    choice([1, 2, 3], draws = 1000),
    choice([4, 5, 6], draws = 1000)
]
""",
"""
(
    choice([1, 2, 3], draws = 1000),
    choice([4, 5, 6], draws = 1000)
)
""",
"""
[
    [
        choice([1, 2, 3], draws = 1000),
        choice([4, 5, 6], draws = 1000)
    ]
]
""",
"""
[
    {
	"b": grid(1, 2),
	"c": choice([6, 7, 8], draws = 1000)
    }
]
""",
]

print "Each stanza should contain five instances:"
for i, spec_str in enumerate(specs):
    print "**********"
    print "Stanza %s:" % i
    son_iterator = genson.loads(spec_str)
    for j, spec in enumerate(son_iterator):
        if j >= 5:
            break
        print "Instance %s" % j
        print spec
    print

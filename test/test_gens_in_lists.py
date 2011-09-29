import genson

specs = [
"""
{
    "a": choice([1, 2, 3], draws = 1000),
    "b": choice([4, 5, 6], draws = 1000)
}
""",
"""
{
    "a": [choice([1, 2, 3], draws = 1000),
          choice([4, 5, 6], draws = 1000)]
}
""",
"""
{
    "a":
    {
	"b": grid(1, 2),
	"c": choice([6, 7, 8], draws = 1000)
    }
}
""",
"""
{
    "a":
    [
	{
	    "b": choice([1, 2, 3, 4], draws=1000),
	    "c": choice([5, 6], draws = 1000)
	}
    ]
}
"""
]

print
print "NOTE: Each stanza below should contain five instances:"
for i, spec_str in enumerate(specs):
    print "**********"
    print "Stanza %s:" % (i+1)
    son_iterator = genson.loads(spec_str)
    for j, spec in enumerate(son_iterator):
        if j >= 5:
            break
        print "Instance %s" % (j+1)
        print spec
    print

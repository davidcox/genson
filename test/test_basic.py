import genson
import time

from os import path
my_path = path.dirname(path.abspath(__file__))


def parse_and_report_error(doc):
    try:
        son_iterator = genson.loads(doc)
    except Exception as e:
        print("Caught exception: %s" % e)
        return

    print("Did not catch exception")


def test_main():

    testdata = """
       {
           "test0": 4,
           "test1" : <0,1,2>,
           "test2" : { "nested": gaussian(0,1,draws=1) },
           "test3" : <"a", "b", uniform(0,1)>,
           ("test4", "test5") : (0, 1),
           ("test6", "test7") : 1,
           ("test8","test9") : <("d", "e"), ("f", "g")>,
           "testA": {"another_nested" : root.test5,
                     "parent_test" : parent.test5},
           "testB": this.test5,
           "testC": this.test2.nested,
           "test_with_underscores": 4,
           "testD": this.test_with_underscores,
           "testE": sin(4),
           "testF": sin(this.testE),
           "testG": 10,
           "testExpr": 2.2*this.testG + (10 / sin(this.testA.another_nested)),
           "testZ": 10
       }
       """
    testdata2 = """
        {
           "test0": 4,
           "test1" : <0,1,2>,
           "test3" : <"a", "b", uniform(0,1)>,
           ("test4", "test5") : (0, 1),
           ("test6", "test7") : 1,
           ("test8","test9") : <("d", "e"), ("f", "g")>
        }
    """

    testdata3 = """
        {
            "test0": [2,3],
            "test1": [-8, this.test0.0, 4],
            "test2":[this.test1.1]
        }
    """

    testdata4 = """
        {
            "test0": [2,-3, -0.4]
        }
    """

    test_broken1 = """
        {
            // no key
            4,
            "test1" : 5
        }
    """

    test_broken2 = """
        {
            // no value
            "test0" :,
            "test1" : 5
        }
    """

    test_broken3 = """
        {
            // no comma
            "test0" : 17
            "test1" : 5
        }
    """

    tic = time.time()
    genson.loads(testdata4)
    toc = time.time() - tic
    print("Negative unary parse time: %s" % toc)

    tic = time.time()
    genson.loads(testdata3)
    toc = time.time() - tic
    print("List placement example parse time: %s" % toc)

    tic = time.time()
    genson.loads(testdata2)
    toc = time.time() - tic
    print("Simple example parse time: %s" % toc)

    tic = time.time()
    son_iterator2 = genson.loads(testdata)
    toc = time.time() - tic
    print("Complex example parse time: %s" % toc)

    for d in son_iterator2:
        print d
    print

    print "Again, but from a formatted file:"
    with open(path.join(my_path, 'test_basic.gson')) as f:
        son_file_iterator = genson.load(f)

    for d in son_file_iterator:
        print d

    parse_and_report_error(test_broken1)
    parse_and_report_error(test_broken2)
    parse_and_report_error(test_broken3)

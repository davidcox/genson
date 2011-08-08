import genson
import time

if __name__ == "__main__":
    
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
      
    tic = time.time()
    son_iterator1 = genson.loads(testdata2)
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
    with open('test.gson') as f:
        son_file_iterator = genson.load(f)

    for d in son_file_iterator:
        print d

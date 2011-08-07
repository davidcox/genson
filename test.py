import genson


if __name__ == "__main__":
    
    testdata = """
       {
           "test0": 4,
           "test1" : <0,1,2>,
           "test2" : { "nested": gaussian(0,1,draws=1) },
           "test3" : <"a", "b", uniform(0,1)>,
           ("test4", "test5") : (0, 1), 
           ("test6", "test7") : 1,
           ("test","test5") : <("d", "e"), ("f", "g")>,
           "testA": {"another_nested" : root.test5,
                     "parent_test" : parent.test5},
           "testB": this.test5,
           "testC": this.test2.nested,
           "test_with_underscores": 4,
           "testD": this.test_with_underscores
       }
       """
    son_iterator = genson.loads(testdata)
    
    for d in son_iterator:
        print d
    print

    print "Again, but from a formatted file:"
    with open('test.gson') as f:
        son_file_iterator = genson.load(f)

    for d in son_iterator:
        print d

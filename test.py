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
           "testA": {"another_nested" : @root.test5 }
       }
       """
    son_iterator = genson.loads(testdata)
    
    for d in son_iterator:
        print d
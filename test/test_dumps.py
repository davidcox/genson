import genson

def test_dumps():
    gson = """
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
    
    gen = genson.loads(gson)
    
    print genson.dumps(gen)
    print genson.dumps(gen, pretty_print=True)
    
    # TODO: obviously, more needed here

if __name__ == "__main__":
    
    test_dumps()


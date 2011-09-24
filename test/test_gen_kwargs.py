import genson

from os import path
my_path = path.dirname(path.abspath(__file__))

def test_gen_kwargs_tuple_bug():
    test_fname = path.join(my_path, 'test_gen_kwargs_tuple_bug.gson')
    with open(test_fname, 'r') as fin:
        genson.load(fin)

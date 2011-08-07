from parser import *
from parameter_generators import *

def isdict(x):
    return isinstance(x, dict)
def istuple(x):
    return isinstance(x, tuple)
def isiterable(x):
    return getattr(x, '__iter__', False)
def isref(x):
    return isinstance(x, ScopedReference)

def jsonify(x, root = None):
    
    if isinstance(x, ParameterGenerator):
        return jsonify(x.value(), root)
    elif isdict(x):
        # build a new copy of the dict
        return_dict = {}
        
        if root is None:
            root = return_dict

        for k,v in x.items():
            val = jsonify(v, root)
                        
            # check if we need to do a splat
            if istuple(k):
                if istuple(val):
                    if len(k) is not len(val):
                        raise Exception("Invalid splat")
                        
                    for (splat_key,splat_val) in zip(k,val):
                        return_dict[splat_key] = jsonify(splat_val, root)
                else:
                    for splat_key in k:
                        return_dict[splat_key] = jsonify(val, root)
            else:
                return_dict[k] = val
            
        return return_dict
    elif isref(x):
        # TODO: more complex logic here
        # for now, just support root level key references
        assert( len(x) == 2 and  x[0] == '@root' )
        key = x[1]
        
        return jsonify( root[key], root )
        
    elif istuple(x):
        return_list = []
        for v in x:
            return_list.append(jsonify(v, root)) 
        return tuple(return_list)
    elif isiterable(x):
        return_list = []
        for v in x:
            return_list.append(jsonify(v, root))       
        return return_list                     
    else:
        return x

class JSONGenerator:
        
    def __init__(self, genson_dict):
        self.genson_dict = genson_dict
        
        self.generators = []
        self.find_generators(genson_dict)
        
        self.first_run = True
    
    def find_generators(self, d):
        vals = d.values()
        for v in vals:
            if isinstance(v, ParameterGenerator):
                self.generators.append(v)
            if isdict(v):
                self.find_generators(v)
    
    def __iter__(self):
        return self
     
     
    def advance_generator_stack(self, cursor=0):
        
        if cursor >= len(self.generators):
            return False
        
        if self.generators[cursor].advance():
            return True
        else:
            self.generators[cursor].reset()
            return self.advance_generator_stack(cursor+1)
        
        
    def next(self):
        
        if self.first_run:
            self.first_run = False
            return jsonify(self.genson_dict)
            
        if self.advance_generator_stack():
            return jsonify(self.genson_dict)
        else:
            self.first_run = True
            raise StopIteration()
            

def load(io):
    s = "\n".join(io.readlines())
    return loads(s)

def loads(genson_string):
    parser = GENSONParser()
    genson_dict = parser.parse_string(genson_string)
    return JSONGenerator(genson_dict)
    


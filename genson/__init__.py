from parser import *
from parameter_generators import *
import copy

def isdict(x):
    return isinstance(x, dict)
def istuple(x):
    return isinstance(x, tuple)
def isiterable(x):
    return getattr(x, '__iter__', False)
def isgensonref(x):
    return isinstance(x, ScopedReference)

def resolve_scoped_reference(ref_obj, context):
    """ Given a reference scope in list format (e.g. ['this', 'key1', 'key2']),
        and a context stack (list of nested dictionary references), resolve
        the reference and return the value
    """
    
    ref = ref_obj.scope_list
    
    if len(context) == 0:
        # TODO: better
        raise Exception("Invalid reference")
    
    # pop an element off of the scope list
    element_to_resolve = ref.pop(0)
    
    if( element_to_resolve == 'root'):
        return resolve_scoped_reference(ref_obj, [context[0]])
    
    if( element_to_resolve == 'parent'):
        return resolve_scoped_reference(ref_obj, context[0:-1])
    
    if( element_to_resolve == 'this'):
        return resolve_scoped_reference(ref_obj, context)
    
    current_context = context[-1]
    
    
    if not isdict(current_context):
        raise Exception("Invalid reference")
    
    if not element_to_resolve in current_context:
        # TODO: make better
        raise Exception("Unknown key: %s" % element_to_resolve)
    
    resolved_element = current_context[element_to_resolve]
    
    if len(ref) != 0:
        context.append(resolved_element)
        return resolve_scoped_reference(ref_obj, context)
    
    return resolved_element

def jsonify(x, context = []):
    
    if isinstance(x, ParameterGenerator):
        return jsonify(x.value(), context)
    elif isdict(x):
        # build a new copy of the dict
        return_dict = {}
        
        # push down object context stack
        context.append(return_dict)

        for k,v in x.items():
            val = jsonify(v, context)
                        
            # check if we need to do a splat
            if istuple(k):
                if istuple(val):
                    if len(k) is not len(val):
                        raise Exception("Invalid splat")
                        
                    for (splat_key,splat_val) in zip(k,val):
                        return_dict[splat_key] = jsonify(splat_val, context)
                else:
                    for splat_key in k:
                        return_dict[splat_key] = jsonify(val, context)
            else:
                return_dict[k] = val
        
        # pop object context stack
        context.pop()
        
        return return_dict
    elif isgensonref(x):
        val = resolve_scoped_reference(copy.deepcopy(x), copy.copy(context))
        return jsonify( val, context )
        
    elif istuple(x):
        return_list = []
        for v in x:
            return_list.append(jsonify(v, context)) 
        return tuple(return_list)
    elif isiterable(x):
        return_list = []
        for v in x:
            return_list.append(jsonify(v, context))       
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
    


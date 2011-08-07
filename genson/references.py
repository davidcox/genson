from internal_ops import GenSONOperand
from util import resolve, isdict
import copy

def resolve_scoped_reference(ref, context):
    """ Given a reference scope in list format (e.g. ['this', 'key1', 'key2']),
        and a context stack (list of nested dictionary references), resolve
        the reference and return the value
    """
    
    
    if len(context) == 0:
        # TODO: better
        raise Exception("Invalid reference")
    
    # pop an element off of the scope list
    element_to_resolve = ref.pop(0)
    
    if( element_to_resolve == 'root'):
        return resolve_scoped_reference(ref, [context[0]])
    
    if( element_to_resolve == 'parent'):
        return resolve_scoped_reference(ref, context[0:-1])
    
    if( element_to_resolve == 'this'):
        return resolve_scoped_reference(ref, context)
    
    current_context = context[-1]
    
    
    if not isdict(current_context):
        raise Exception("Invalid reference")
    
    if not element_to_resolve in current_context:
        # TODO: make better
        raise Exception("Unknown key: %s" % element_to_resolve)
    
    resolved_element = current_context[element_to_resolve]
    
    if len(ref) != 0:
        context.append(resolved_element)
        return resolve_scoped_reference(ref, context)
    
    return resolved_element


class ScopedReference (GenSONOperand):
    def __init__(self, scope_list):
        self.scope_list = scope_list
    
    def __genson_eval__(self, context):
        return resolve_scoped_reference( copy.deepcopy(self.scope_list), 
                                         copy.copy(context) )

from internal_ops import GenSONOperand
from util import resolve, isdict, isindexable, genson_dumps
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

    if (element_to_resolve == 'root'):
        return resolve_scoped_reference(ref, [context[0]])

    if (element_to_resolve == 'parent'):
        return resolve_scoped_reference(ref, context[0:-1])

    if (element_to_resolve == 'this'):
        return resolve_scoped_reference(ref, context)

    current_context = context[-1]

    if isdict(current_context):
        if not element_to_resolve in current_context:
            # TODO: make better
            raise Exception("Unknown key: %s" % element_to_resolve)
    elif isindexable(current_context):
        element_to_resolve = int(element_to_resolve)
        if not 0 <= element_to_resolve < len(current_context):
            raise Exception("Reference index out of range: %d" %
                                                  element_to_resolve)
    else:
        raise Exception("Invalid reference")

    resolved_element = current_context[element_to_resolve]

    if len(ref) != 0:
        context.append(resolved_element)
        return resolve_scoped_reference(ref, context)

    return resolved_element


class ScopedReference (GenSONOperand):
    def __init__(self, scope_list):
        self.scope_list = scope_list

    def __genson_eval__(self, context):
        return resolve_scoped_reference(copy.deepcopy(self.scope_list),
                                         copy.copy(context))

    def __genson_repr__(self, pretty_print=False, depth=0):
        return ".".join(self.scope_list)


def ref(ref_str):
    "A helper to convert a genson ref string into a SopeReference object"
    return ScopedReference(ref_str.split('.'))

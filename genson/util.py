# import references
import copy


def isdict(x):
    return isinstance(x, dict)
def istuple(x):
    return isinstance(x, tuple)
def isiterable(x):
    return getattr(x, '__iter__', False)
# def isgensonref(x):
#     return isinstance(x, ScopedReference)
def isgensonevaluable(x):
    return getattr(x, '__genson_eval__', False)




def resolve(x, context = []):
    if isgensonevaluable(x):
        return resolve(x.__genson_eval__(context), context)
    elif isdict(x):
        # build a new copy of the dict
        return_dict = {}

        # push down object context stack
        context.append(return_dict)

        for k,v in x.items():
            val = resolve(v, context)

            # check if we need to do a splat
            if istuple(k):
                if istuple(val):
                    if len(k) is not len(val):
                        raise Exception("Invalid splat")

                    for (splat_key,splat_val) in zip(k,val):
                        return_dict[splat_key] = resolve(splat_val, context)
                else:
                    for splat_key in k:
                        return_dict[splat_key] = resolve(val, context)
            else:
                return_dict[k] = val

        # pop object context stack
        context.pop()

        return return_dict
    # elif isgensonref(x):
    #     val = resolve_scoped_reference(copy.deepcopy(x), copy.copy(context))
    #     return resolve( val, context )

    elif istuple(x):
        return_list = []
        for v in x:
            return_list.append(resolve(v, context))
        return tuple(return_list)
    elif isiterable(x):
        return_list = []
        for v in x:
            return_list.append(resolve(v, context))
        return return_list
    else:
        return x

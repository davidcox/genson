# import references
import copy

default_random_seed = None


def set_global_seed(new_seed):
    global default_random_seed
    default_random_seed = new_seed


def get_global_seed():
    global default_random_seed
    return default_random_seed


def isdict(x):
    return isinstance(x, dict)


def istuple(x):
    return isinstance(x, tuple)


def isindexable(x):
    return getattr(x, '__getitem__', False)


def isiterable(x):
    return getattr(x, '__iter__', False)
# def isgensonref(x):
#     return isinstance(x, ScopedReference)


def isgensonevaluable(x):
    return getattr(x, '__genson_eval__', False)


def isgensondumpable(x):
    return getattr(x, '__genson_repr__', False)


def resolve(x, context=None):

    if context is None:
        context = [x]

    # if the object "knows what to do", let it
    if isgensonevaluable(x):
        return resolve(x.__genson_eval__(context), context)

    # a nested JSON object
    elif isdict(x):
        return_dict = x

        # push down the dict onto the context stack
        # context.append(return_dict)
        context.append(x)

        for k, v in x.items():
            val = resolve(v, context)

            # check if we need to do a "splat"
            if istuple(k):
                if istuple(val):
                    if len(k) is not len(val):
                        raise Exception("Invalid splat")

                    for (splat_key, splat_val) in zip(k, val):
                        return_dict[splat_key] = resolve(splat_val, context)
                else:
                    for splat_key in k:
                        return_dict[splat_key] = resolve(val, context)
                x.pop(k)
            else:
                return_dict[k] = val

        # pop object context stack
        context.pop()

        return return_dict

    elif istuple(x):
        return_list = list(x)
        for i, v in enumerate(x):
            return_list[i] = resolve(v, context)
        return tuple(return_list)

    elif isiterable(x):
        return_list = x
        for i, v in enumerate(x):
            return_list[i] = (resolve(v, context))
        return return_list
    else:
        return x


def genson_dumps(o, pretty_print=False, depth=0):

    if isgensondumpable(o):
        return o.__genson_repr__(pretty_print, depth)

    elif isdict(o):

        element_strs = []
        for k, v in o.items():
            if isiterable(k):
                element_strs.append('(%s) : %s' % \
                                    (",".join(['"%s"' % x for x in k]),
                                    genson_dumps(v, pretty_print, depth + 1)))
            else:
                element_strs.append('"%s" : %s' % \
                        (k, genson_dumps(v, pretty_print, depth + 1)))

        return_str = ''
        if pretty_print:
            tabs = '\t' * depth
            return_str += '{\n' + tabs + '\t'
            return_str += (",\n" + tabs + "\t").join(element_strs)

            return_str += '\n' + tabs + '}'
        else:
            return_str = "{%s}" % ",".join(element_strs)
        return return_str

    elif isiterable(o):
        return '(%s)' % (
                ', '.join([genson_dumps(x, pretty_print, depth) for x in o]))
    else:
        return str(o)


def kwargs_consumed(f):
    def wrapper(self, *args, **kwargs):
        f(self, *args, **kwargs)
        assert_kwargs_consumed(kwargs)
    return wrapper


def assert_kwargs_consumed(kwargs):
    if len(kwargs) > 0:
        raise ValueError(('Unknown keyword arguments: %s' %
                          ', '.join(kwargs.keys())))

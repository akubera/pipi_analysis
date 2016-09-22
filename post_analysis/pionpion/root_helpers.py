#
# post_analysis/pionpion/root_helpers.py
#

import sys


def get_root_object(obj, paths):
    """
    Return a root object contained in the obj
    """
    if isinstance(paths, (list, tuple)):
        for path in paths:
            found = get_root_object(obj, path)
            if found != None:
                return found
        return None

    key, *rest = paths.split('.', 1)

    try:
        new_obj = obj.Get(key)
    except AttributeError:
        new_obj = obj.FindObject(key)

    if rest:
        return get_root_object(new_obj, rest[0])
    else:
        return new_obj

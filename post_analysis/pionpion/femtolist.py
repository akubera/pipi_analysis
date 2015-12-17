#
# pionpion/femtolist.py
#

from .root_helpers import get_root_object
from .analysis import Analysis


class Femtolist:
    """
    Class wrapping functionality of the femtolist object - the results in a
    root file.
    """

    FEMTOLIST_PATHS = [
        'femtolist',
        'PWG2FEMTO.femtolist',
    ]

    def __init__(self, file):
        femtolist = get_root_object(file, self.FEMTOLIST_PATHS)
        if femtolist == None:
            raise ValueError("Could not find a femtolist in %r" % (file))

        self._femtolist = femtolist

    def __iter__(self):
        for analysis in self._femtolist:
            yield Analysis(analysis)

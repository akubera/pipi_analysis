#
# pionpion/analysis.py
#

from .root_helpers import get_root_object
from ROOT import TObjArray


class Analysis:

    def __init__(self, analysis_obj):
        if not isinstance(analysis_obj, TObjArray):
            raise ValueError("Analysis expected TObjArray initialization value. Found %r" % (analysis_obj))

        self._data = analysis_obj

    def __getattr__(self, name):
        """
        Forwards any missing attribute to the underlaying TObjArray
        """
        return getattr(self._data, name)

    def __getitem__(self, name):
        """
        Returns the object found at the path given in the name.
        """
        return get_root_object(self._data, name)

#
# pionpion/analysis.py
#

from .root_helpers import get_root_object
from collections import defaultdict
from ROOT import (
    TObjArray,
    TObjString,
)


class Analysis:
    """
    Analysis object wrapping a TObjArray full of various femtoscopic
    information.
    """

    def __init__(self, analysis_obj):
        if not isinstance(analysis_obj, TObjArray):
            raise ValueError("Analysis expected TObjArray initialization value. Found %r" % (analysis_obj))

        self._data = analysis_obj
        self.metadata = Analysis.load_metadata(self._data.Last())

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

    @staticmethod
    def load_metadata(settings):
        if not isinstance(settings, TObjString):
            return

        def tree(): return defaultdict(tree)
        analysis_meta = tree()

        analysis_meta
        for s in str(settings).split("\n")[1:-1]:
            k, v = s.split('=')
            keys = k.split('.')
            k = analysis_meta
            for key in keys[:-1]:
                k = k[key]
            k[keys[-1]] = v
            # for key in k.split('.'):
        return analysis_meta

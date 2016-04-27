#
# pionpion/analysis.py
#

from stumpy import Histogram
from collections import defaultdict
from .root_helpers import get_root_object
from ROOT import (
    TObjArray,
    TObjString,
)


class Analysis:
    """
    Analysis object wrapping a TObjArray full of various femtoscopic
    information.
    """

    QINV_NUM_PATH = ['Num_qinv_pip', 'Num_qinv_pim']
    QINV_DEN_PATH = ['Den_qinv_pip', 'Den_qinv_pim']

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

    @property
    def name(self):
        return self._data.GetName()

    @property
    def system_name(self):
        """
        Returns the 'friendly' name of the particle system - could be π+, π-
        """
        pp_info = self.metadata['AliFemtoAnalysisPionPion']
        if pp_info:
            if 'pion_1_type' in pp_info:
                pion_code = int(pp_info['pion_1_type'])
            elif 'piontype' in pp_info:
                pion_code = int(pp_info['piontype'])

        return {
            0: "π^{+}",
            1: "π^{-}",
        }[pion_code]

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

    @property
    def qinv_pair(self):
        n = get_root_object(self._data, self.QINV_NUM_PATH)
        d = get_root_object(self._data, self.QINV_DEN_PATH)
        return Histogram.BuildFromRootHist(n), Histogram.BuildFromRootHist(d)

#
# pionpion/analysis.py
#

import itertools

from stumpy import Histogram
from collections import defaultdict
from .root_helpers import get_root_object
from ROOT import (
    TObjArray,
    TObjString,
    TFile,
    TDirectory,
    TList,
    TKey,
)


class Analysis:
    """
    Analysis object wrapping a TObjArray full of various femtoscopic
    information.
    """

    QINV_NUM_PATH = ['Num_qinv_pip', 'Num_qinv_pim']
    QINV_DEN_PATH = ['Den_qinv_pip', 'Den_qinv_pim']
    KT_BINNED_ANALYSIS_PATH = ['KT_Qinv']

    def __init__(self, analysis_obj):
        if isinstance(analysis_obj, TObjArray):
            pass
        elif isinstance(analysis_obj, TDirectory):
            array = TObjArray()
            array.SetName(analysis_obj.GetName())
            for k in analysis_obj.GetListOfKeys():
                array.Add(k.ReadObj())
            analysis_obj = array
        else:
            raise ValueError("Analysis expected TObjArray or TDirectory "
                             "initialization value. Found %r." % (analysis_obj))

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

    def has_kt_bins(self):
        """
        Return if the analysis has a collection of kt-binned histograms
        """
        return get_root_object(self._data, self.KT_BINNED_ANALYSIS_PATH) != None

    @property
    def name(self):
        return self._data.GetName()

    @property
    def title(self):
        x = self.name.split('_')
        centrality_name = "%d-%d%%" % tuple(map(int, x[1:3]))
        title = "%s (%s)" % (self.system_name, centrality_name)
        return title.replace("π", "#pi")

    @property
    def system_name(self):
        """
        Returns the 'friendly' name of the particle system - could be π+, π-
        """
        if self.metadata:
            pp_info = self.metadata['AliFemtoAnalysisPionPion']
        else:
            suffix = self.name.split('_')[-1]
            pp_info = {'pion_1_type': 0}
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
        if n == None:
            print("Error! Could not load numerator in analysis")
            n = None
        else:
            n = Histogram.BuildFromRootHist(n)

        d = get_root_object(self._data, self.QINV_DEN_PATH)
        if d == None:
            print("Error! Could not load denominator in analysis")
            d = None
        else:
            d = Histogram.BuildFromRootHist(d)

        return n, d

    @property
    def kt_binned_pairs(self):
        """
        Return the TObjArray containing the kT binned pairs
        """
        try:
            return self._kt_binned_correlation_functions
        except AttributeError:
            pass
        kt_cfs = get_root_object(self._data, self.KT_BINNED_ANALYSIS_PATH)

        if isinstance(kt_cfs, TDirectory):
            kt_cfs = list(map(TKey.ReadObj, kt_cfs.GetListOfKeys()))
        elif kt_cfs == None:
            kt_cfs = ()

        self._kt_binned_correlation_functions = kt_cfs
        return kt_cfs

    def qinv_pair_in_kt_bin(self, idx):
        """
        """
        if isinstance(idx, str):
            objarray = self.kt_binned_pairs.FindObject(idx)
        else:
            objarray = self.kt_binned_pairs[idx]
        n = get_root_object(objarray, self.QINV_NUM_PATH)
        d = get_root_object(objarray, self.QINV_DEN_PATH)
        return Histogram.BuildFromRootHist(n), Histogram.BuildFromRootHist(d)

    def apply_momentum_correction_matrix(self, matrix):
        """
        Apply the momentum correction smearing matrix to all relevant histograms.

        Args:
            matrix: The normalized square matrix which smears the q_inv histograms.
        """
        def apply_matrix(root_hist):
            hist = Histogram.BuildFromRootHist(root_hist)
            data = hist.__rmatmul__(matrix).copy_data_with_overflow()
            root_hist.SetContent(data)

        def apply_vector(root_hist):
            hist = Histogram.BuildFromRootHist(root_hist)
            data = hist.data * matrix
            root_hist.SetContent(data)

        def get_num_and_den(obj):
            yield get_root_object(obj, self.QINV_NUM_PATH)
            yield get_root_object(obj, self.QINV_DEN_PATH)

        def get_num_and_den_in_collection(obj):
            for tobj in obj:
                yield from get_num_and_den(tobj)

        # keys = [self.QINV_NUM_PATH, self.QINV_DEN_PATH]
        # keys += list(map(lambda x:  self.kt_binned_pairs)
        objs = list(get_num_and_den(self._data))
        for kt_bin_cf in self.kt_binned_pairs:
            objs += list(get_num_and_den(kt_bin_cf))

        apply = apply_vector if matrix.ndim == 1 else apply_matrix

        for obj in filter(lambda x: x is not None, objs):
            apply(obj)

    def write_into(self, output):
        """
        Write the analysis object into some kind of output
        """

        copied_settings = False
        def recursive_root_write(obj, container):
            nonlocal copied_settings

            if isinstance(obj, TDirectory):
                obj = map(TKey.ReadObj, obj.GetListOfKeys())

            for o in obj:
                container.cd()
                # special case for my analysis! only copies the first TObjString found
                if isinstance(o, TObjString):
                    if copied_settings:
                        continue
                    copied_settings = True

                elif isinstance(o, TObjArray):
                    if isinstance(container, TDirectory):
                        sub_dir = container.mkdir(o.GetName())
                        recursive_root_write(o, sub_dir)

                    elif isinstance(container, TObjArray):
                        sub_container = TObjArray()
                        sub_container.SetName(o.GetName())
                        sub_container.SetOwner(True)
                        recursive_root_write(o, sub_container)

                elif isinstance(container, TDirectory):
                    o.Clone().Write()
                else:
                    container.Add(o.Clone())

        if isinstance(output, TDirectory):
            container = output.mkdir(self.name)
            recursive_root_write(self._data, container)
            return container

        elif isinstance(output, (TList, TObjArray)):
            container = TObjArray()
            container.SetName(self.name)
            container.SetOwner(True)
            recursive_root_write(self._data, container)
            output.Add(container)

        else:
            raise NotImplementedError

#
# pionpion/femtolist.py
#

from .root_helpers import get_root_object
from .analysis import Analysis
import ROOT


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
        if isinstance(file, str):
            file = ROOT.TFile(file, "READ")

        femtolist = get_root_object(file, self.FEMTOLIST_PATHS)
        if femtolist == None:
            raise ValueError("Could not find a femtolist in %r" % (file))

        self._femtolist = femtolist
        self._file = file

    def __iter__(self):
        if isinstance(self._femtolist, ROOT.TDirectoryFile):
            femto_iter = map(ROOT.TKey.ReadObj, self._femtolist.GetListOfKeys())
        else:
            femto_iter = self._femtolist

        for analysis in femto_iter:
            yield Analysis(analysis)

    def __getitem__(self, idx):
        """
        Return an analysis object either by numerical index or by name.
        If no analysis exists, an IndexError is raised.
        """
        if isinstance(idx, int):
            obj = self._femtolist.At(idx)
        elif isinstance(idx, str):
            obj = self._femtolist.FindObject(idx)
        else:
            obj = None

        if obj == None:
            raise IndexError("No analysis found with index `{}`".format(idx))
        return Analysis(obj)

    @property
    def name(self):
        return 'femtolist'

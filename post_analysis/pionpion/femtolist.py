#
# pionpion/femtolist.py
#

from stumpy.utils import get_root_object, is_null
from .analysis import Analysis
from os.path import basename
import ROOT


class Femtolist:
    """
    Class wrapping functionality of the femtolist object - the results in a
    root file.
    """

    FEMTOLIST_PATHS = [
        'femtolist',
        'PWG2FEMTO.femtolist',
        'PWG2FEMTO.pionpion_femtolist',

        'PWG2FEMTO',
    ]

    def __init__(self, file, listpath=None):
        """
        Construct femtolist from file; given either a TFile or the
        path to the file.
        If no femtolist object is found inside the file - a ValueError
        is raised.
        """
        if not isinstance(file, ROOT.TDirectory):
            file = ROOT.TFile(str(file), "READ")

        # find the femtolist
        if listpath is None:
            listpath = self.FEMTOLIST_PATHS
        femtolist = get_root_object(file, listpath)
        if femtolist == None:
            raise ValueError("Could not find a femtolist in %r" % (file))

        self._femtolist = femtolist
        self._file = file

    def __iter__(self):
        """
        Iterate over all analyses in this Femtolist
        """
        if isinstance(self._femtolist, ROOT.TDirectoryFile):
            femto_iter = map(ROOT.TKey.ReadObj, self._femtolist.GetListOfKeys())
        else:
            femto_iter = self._femtolist

        for analysis in femto_iter:
            yield Analysis(analysis)

    def __getitem__(self, idx):
        """
        Return an analysis object either by numerical index or by name.
        If no analysis exists, an KeyError is raised.
        """
        if isinstance(idx, int):
            obj = self._femtolist.At(idx)
        elif isinstance(idx, str):
            obj = self._femtolist.FindObject(idx)
        elif isinstance(idx, slice):
            return [Analysis(obj) for obj in self._femtolist[idx]]
        else:
            obj = None

        if is_null(obj):
            raise KeyError("No analysis found with index `{}`".format(idx))

        return Analysis(obj)

    @property
    def name(self):
        return self._femtolist.GetName()

    @property
    def filepath(self):
        return self._file.GetName()

    @property
    def filename(self):
        return basename(self.filepath)

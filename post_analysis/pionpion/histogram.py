#
# pionpion/histogram.py
#
"""
Histogram helper methods.
"""

import root_numpy
import numpy as np

import functools
import itertools
from itertools import starmap


class Histogram:
    """
    A class wrapping TH[123][FD] root histograms - providing an easier to use
    and more pythonic interface.
    """

    # The pointer to the underlying histogram object
    _ptr = None

    def __init__(self, hist):
        self._ptr = hist
        self.data = root_numpy.hist2array(self._ptr, include_overflow=True)
        # add two overflow bins
        error_shape = np.array(list(self.data.shape)) + [2, 2, 2]
        error_shape = self.data.shape
        errors = root_numpy.array(self._ptr.GetSumw2())
        self.error = np.sqrt(errors).reshape(error_shape)
        # print(">>", self.error[4, 4, 4])
        # print(">>", hist.GetBinError(4, 4, 4))
        self._axes = (hist.GetXaxis(), hist.GetYaxis(), hist.GetZaxis())
        self._axes = Histogram.Axis.BuildFromHist(hist)
        self._axis_data = np.array(list(
            [axis.GetBinCenter(i) for i in range(1, axis.GetNbins() + 1)]
            for axis in self._axes
        ))
        self.mask = Histogram.Mask(self)

    @property
    def shape(self):
        return self.data.shape

    # @functools.lru_cache
    def __getitem__(self, val):
        """
        Returns the value of bin specified by value val. If val is a float, the
        corresponding bin is searched for automatically and the value returned
        """
        if isinstance(val, tuple):
            val = tuple(axis.getbin(v) for v, axis in zip(val, self._axes))
        else:
            val = self._axes[0].getbin(val)
        return self.data[val]

    def domain(self, *ranges):
        ranges = tuple(axis.getbin(x) for axis, x in zip(self._axes, ranges))
        itertools.product(ranges)

    def bin_at(self, x, y=0.0, z=0.0):
        return tuple(axis.bin_at(a) for axis, a in zip(self._axes, (x, y, z)))

    def value_at(self, x, y=0.0, z=0.0):
        i, j, k = self.bin_at(x, y, z)
        print("[value_at]", (x, y, z), (i,j,k))
        return self.data[i, j, k]

    def value_in(self, i, j=0, k=0):
        print("[value_in]", (i,j,k))
        return self.data[i, j, k]


    class Axis:
        """
        Histogram axis abstraction. Wraps a TAxis
        """

        def __init__(self, root_TAxis):
            self._ptr = root_TAxis

            if not self._ptr.IsVariableBinSize():
                maxbin = self._ptr.GetNbins()
                self.data = np.linspace(self._ptr.GetBinCenter(0),
                                        self._ptr.GetBinCenter(maxbin),
                                        maxbin + 1)
            else:
                self.data = root_numpy.array(self._ptr.GetXbins())

        def searchsorted(self, value, side, sorter):
            return self.data.searchsorted(value, side, sorter)

        def search(self, value):
            idx = np.searchsorted(self.data, value, side="left")
            rval, lval = array[idx - 1:idx + 1]
            return rval if fabs(value - rval) < fabs(value - lval) else lval

        @classmethod
        def BuildFromHist(self, hist):
            """
            Returns tuple of 3 Axis objects, corresponding to the x,y,z axes of
            the hist argument
            """
            axes = (hist.GetXaxis(), hist.GetYaxis(), hist.GetZaxis())
            return tuple(map(Histogram.Axis, axes))

        def __getattr__(self, attr):
            """
            Forwards any attribute requests to the real axis object
            """
            return getattr(self._ptr, attr)

        def bin_at(self, value):
            self._ptr
            return self._ptr.FindBin(value)

        def getbin(self, value):
            """
            Return the bin relating to value
            """
            if isinstance(value, float):
                return self._ptr.FindBin(value)
            if isinstance(value, slice):
                return slice(*map(self.getbin, (value.start, value.stop)))

            return value

        def bin_generator(self, values):
            print(l)

        def domain(self, space):
            return np.array(map(self._ptr.GetBinCenter, space))


    class Mask:
        """
        A class wrapping a numpy array-mask used for keeping same shape between
        data and error arrays
        """

        def __init__(self, hist):
            self.hist = hist

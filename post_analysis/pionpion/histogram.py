#
# pionpion/histogram.py
#
"""
Histogram helper methods.
"""

import root_numpy
import numpy as np

import functools


class Histogram:
    """
    A class wrapping TH[123][FD] root histograms - providing an easier to use
    and more pythonic interface.
    """

    # The pointer to the underlying histogram object
    _ptr = None

    def __init__(self, obj):
        self._ptr = obj
        self.data = root_numpy.hist2array(self._ptr)
        self.error = root_numpy.array(self._ptr.GetSumw2())
        print(self.error)
        self._axes = (hist.GetXaxis(), hist.GetYaxis(), hist.GetZaxis())
        self._axis_data = np.array(list(
            [axis.GetBinCenter(i) for i in range(1, axis.GetNbins() + 1)]
            for axis in self._axes
        ))

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


    class Axis:
        """
        Histogram axis abstraction. Wraps a TAxis
        """

        def __init__(self, root_TAxis):
            self._ptr = root_TAxis

            self.data = root_numpy.array(self._ptr.GetXbins())

        @classmethod
        def BuildFromHist(self, hist):
            """
            Returns tuple of 3 Axis objects, corresponding to the x,y,z axes of
            the hist argument
            """
            axes = (hist.GetXaxis(), hist.GetYaxis(), hist.GetZaxis())
            return tuple(map(Axis, axes))


        def __getattr__(self, attr):
            """
            Forwards any attribute requests to the real axis object
            """
            return getattribute(self._ptr, attr)

        def getbin(self, value):
            """
            Return the bin relating to value
            """
            if isinstance(value, float):
                return self._ptr.FindBin(value)
            if isinstance(value, slice):
                return slice(*map(self.getbin, value[:2]))

            return value

        def domain(self, space):
            return np.array(map(self._ptr.GetBinCenter, space))

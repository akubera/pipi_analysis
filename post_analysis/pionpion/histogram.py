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
        # error_shape = np.array(list(self.data.shape)) + [2, 2, 2]
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
        assert self.data.shape == tuple(a.data.shape[0] for a in self._axes)
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
        if ranges is ():
            domains = iter(axis.domain() for axis in self._axes)
        else:
            axis_range_pairs = zip(self._axes, ranges)
            domains = iter(axis.domain(r) for axis, r in axis_range_pairs)
        return itertools.product(*domains)

    def bounded_domain(self, *ranges):
        """
        Return a numpy array containing the bin centers of the range that
        this axis' domain.
        """
        if ranges is ():
            domains = iter(axis.domain() for axis in self._axes)
        else:
            axis_range_pairs = zip(self._axes, ranges)
            domains = iter(axis.bounded_domain(r) for axis, r in axis_range_pairs)

        return np.array([l for l in itertools.product(*domains)])

    def bin_ranges(self, *ranges):
        """
        zips ranges with axes to generate bin_ranges
        """
        return tuple(a.getbin(r) for a, r in zip(self._axes, ranges))

    def centered_bin_ranges(self, *ranges, expand=False, inclusive=False):
        """
        Applies centered_bin_range_pair to each axis. Returns tuple of integer
        pairs, or if expand is True, returns one flattened tuple of ints.
        """
        res = []
        for r, a in zip(ranges, self._axes):
            if r is not None:
                val = a.centered_bin_range_pair(*r)
                if inclusive:
                    val = val[0], val[1] - 1
                res.append(val)
            else:
                res.append(((), ()))

        if expand:
            return tuple(x for x in res for x in x)
        return res

    def bin_at(self, x, y=0.0, z=0.0):
        return tuple(axis.bin_at(a) for axis, a in zip(self._axes, (x, y, z)))

    def getslice(self, x, y=0.0, z=0.0):
        return tuple(axis.getslice(a) for axis, a in zip(self._axes, (x, y, z)))

    def value_at(self, x, y=0.0, z=0.0):
        i, j, k = self.bin_at(x, y, z)
        return self.data[i, j, k]

    def value_in(self, i, j=0, k=0):
        return self.data[i, j, k]

    def project_1d(self, axis_idx, *axis_ranges, bounds=(None, None)):
        """
        Project multi-dimensional data into one dimention along axis with
        index 'axis_idx'. The variable 'axis_ranges' parameter limits the
        range of all other axes, with the position of each axis_range
        corresponding to each axis NOT the axis being projected into.
        For example:

            # projects onto x-axis, y is limited between (1.0, 2.0), z (-1.0, 1.0)
            hist.project_1d(0, (1.0, 2.0), (-1.0, 1.0))

            # projects onto y-axis, x is limited between (1.0, 2.0), z (-1.0, 1.0)
            hist.project_1d(1, (1.0, 2.0), (-1.0, 1.0))

        The optional 'bounds' variable is the limit of the projected axis; this
        defaults to no-limit
        """
        assert 0 <= axis_idx < self.data.ndim

        # merge specified boundries with infinite slice(None) generator
        bounds = itertools.chain(axis_ranges, itertools.repeat(slice(None)))

        ranges = []
        summed_axes = []

        axes = self._axes
        for i, axis in enumerate(self._axes):
            if i == axis_idx:
                ranges.append(axis.getslice(bounds))
            else:
                s = axis.getslice(next(bounds))
                ranges.append(s)
                if isinstance(s, slice):
                    summed_axes.append(i)

        res = self.data[ranges].sum(axis=tuple(summed_axes))
        print('res:', res)
        return res

    def project_2d(self, axis_x, axis_y, *axis_ranges, bounds_x=slice(None), bounds_y=slice(None)):
        """
        Project the histogram into 2 dimensions.
        """
        assert axis_x != axis_y
        assert 0 <= axis_x < self.data.ndim
        assert 0 <= axis_y < self.data.ndim

        bounds = itertools.chain(axis_ranges, itertools.repeat(slice(None)))
        ranges = []
        summed_axes = []
        for i, axis in enumerate(self._axes):
            if i == axis_x:
                ranges.append(axis.getslice(bounds_x))
            elif i == axis_y:
                ranges.append(axis.getslice(bounds_y))
            else:
                s = axis.getslice(next(bounds))
                ranges.append(s)
                if isinstance(s, slice):
                    summed_axes.append(i)

        return self.data[ranges].sum(axis=tuple(summed_axes))

    def __str__(self):
        return '<{dim}D Histogram "{name}" ({sizes}) at {id}>'.format(
            name=self._ptr.GetName(),
            dim=self.data.ndim,
            sizes="-".join(map(str, self.data.shape)),
            id="0x%x" % id(self),
        )

    #
    # Math Functions
    #
    def __truediv__(self, rhs):
        if isinstance(rhs, Histogram):
            quotient = self._ptr.Clone()
            quotient.Divide(rhs._ptr)
            q = Histogram(quotient)
            return q
        elif isinstance(rhs, float):
            clone = self._ptr.Clone()
            clone.Scale(1.0 / rhs)
            return Histogram(clone)
        else:
            raise TypeError("Cannot divide histogram by %r" % rhs)

    class Axis:
        """
        Histogram axis abstraction. Wraps a TAxis
        """

        def __init__(self, root_TAxis):
            self._ptr = root_TAxis
            if not self._ptr.IsVariableBinSize():
                maxbin = self._ptr.GetNbins() + 1
                self.data = np.linspace(self._ptr.GetBinCenter(0),
                                        self._ptr.GetBinCenter(maxbin),
                                        maxbin + 1)
                assert all(self._ptr.GetBinCenter(i) - self.data[i] < 1e-9
                           for i in (0, 1, maxbin // 2, maxbin - 2))
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

        def __getitem__(self, index):
            """
            Returns the value of bin specified by index
            """
            return self.data[index]

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
            if isinstance(value, (tuple, list)):
                start, stop = map(self.getbin, value)
                if isinstance(stop, int):
                    stop += 1
                return slice(start, stop)

            return value

        def getslice(self, value):
            """
            Alias of getbin
            """
            return self.getbin(value)

        def bin_range_pair(self, value):
            """
            Returns a pair (tuple) of integers representing the beginning
            and (exclusive) ending of the range of bins containing the value(s)
            in value. If value is a floating point, this returns the bin in
            which this value can be found, and the 'next' bin.
            """
            asbins = self.getbin(value)
            if isinstance(asbins, int):
                start = asbins
                stop = asbins + 1
            elif isinstance(asbins, slice):
                start = asbins.start
                stop = asbins.start + 1
            else:
                raise ValueError("Cannot find bin_range_pair of %s" % (value))
            return start, stop

        def bin_range(self, value):
            """
            Returns a range object which returns the bins specified by the
            argument. If value is a floating point number, the range will return
            only the bin the value falls into. If value is an integer, range
            will only return that value. If value is a pair (tuple or list) of
            floats or ints, the range interates through all bins falling
            between the two bins.
            """
            start, stop = self.bin_range_pair(value)
            return range(start, stop)

        def centered_bin_range_pair(self, value=0.0, width=1):
            """
            Returns a pair (tuple) of integers representing the beginning
            and (exclusive) ending of the range of bins centered around the
            bin containing the value parameter. The width parameter shifts the
            bins above and below the value.

            The range will be $2 * 'width' + 1$ long.
            """
            start, stop = self.bin_range_pair(value)
            start -= width
            stop += width
            return start, stop

        def domain(self, n=None):
            """
            Return a numpy array containing the floating point values within
            this axis' domain. If no 'n' parameter is specified, this is a copy
            of the data axis' data
            """
            if n is None:
                return np.copy(self.data)
            else:
                return np.linspace(n, self.data[0], self.data[-1])

        def bounded_domain(self, value):
            """
            Return a numpy array containing the bin centers of the range that
            this axis' domain.
            """
            s = self.getslice(value)
            return self.data[s]


    class Mask:
        """
        A class wrapping a numpy array-mask used for keeping same shape between
        data and error arrays
        """

        def __init__(self, hist):
            self.hist = hist

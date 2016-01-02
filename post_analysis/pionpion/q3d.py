#
# post_analysis/pionpion/q3d.py
#
"""
Module with classes and functions for dealing with the three dimentional
histograms containing Q_out Q_side Q_long particle data
"""

import root_numpy
import numpy as np
import numpy.ma as ma
from itertools import starmap


class Q3D:
    """
    Class wrapping a Q_{out,side,long} histogram for easy access
    """

    def __init__(self, hist):
        self._hist = hist
        self._data = root_numpy.hist2array(hist)
        self._axes = (hist.GetXaxis(), hist.GetYaxis(), hist.GetZaxis())
        self._axis_data = np.array(list(
            list(axis.GetBinCenter(i) for i in range(1, axis.GetNbins() + 1))
            for axis in self._axes
        ))

    def bins_to_slices(self,
                       x_domain=(None, None),
                       y_domain=(None, None),
                       z_domain=(None, None)):
        """
        Return a triple of pairs, each containing
        """
        def contains_float(a):
            return any(isinstance(x, float) for x in a)

        def domain_to_bins(axis, dom):
            if contains_float(dom):
                # FindBin returns axis bin, which is one ahead of the array bin
                # (i.e. hist.GetBinContent(1) == data[0])
                # Decrement first index, leave second as it points to excluded
                # range end
                bin1 = axis.FindBin(dom[0]) - 1
                bin2 = axis.FindBin(dom[1])
                bin1 = np.searchsorted(self._axis_data[1], dom[0])
                bin1 = np.searchsorted(self._axis_data[1], dom[1], side='right')
                return (bin1, bin2)
            else:
                return dom

        def dom_to_slice(axis, dom):
            bins = domain_to_bins(axis, dom)
            return slice(*bins)

        domain_tuples = (x_domain, y_domain, z_domain)
        slices = tuple(starmap(dom_to_slice, zip(self._axes, domain_tuples)))
        print("slices:", slices)
        return slices

    def projection_out(self, y_domain=(-.01, 0.5), z_domain=(-.01, 0.1)):
        """
        Returns a numpy array of the entire 'out' axis, with the other two axes
        restricted by the parameters
        """
        # change domains into array slices
        x_slice, y_slice, z_slice = self.bins_to_slices(
            y_domain=y_domain,
            z_domain=z_domain
        )

        data = self._data[x_slice, y_slice, z_slice]
        # print("Sliced data", data.shape)
        # print(data)
        sum = data.sum(axis=(1, 2))
        # print("Sum: ", sum.shape)
        # print(sum)
        return sum

    def projection_side(self, x_domain=(-0.1, 0.1), z_domain=(-0.1, 0.1)):
        """
        Returns a numpy array of the entire 'side' axis, with the other two
        axes restricted by the parameters
        """
        x_slice, y_slice, z_slice = self.bins_to_slices(
            x_domain=x_domain,
            z_domain=z_domain
        )

        data = self._data[x_slice, y_slice, z_slice]
        sum = data.sum(axis=(0, 2))
        return sum

    def get_projection(self, x_slice, y_slice, z_slice):
        """
        Returns a numpy array
        """
        data = self._data[x_slice, y_slice, z_slice]

        if (x_slice)

        sum = data.sum(axis=(1,2))

        q = np.abs(self._axis_data[1]) < 0.034
        print(q)
        print(self._data[:,q,:])
        data = self._data[x_slice, y_slice, z_slice]
        # print("Sliced data", data.shape)
        # print(data)
        sum = data.sum(axis=(1,2))
        # print("Sum: ", sum.shape)
        # print(sum)
        return sum

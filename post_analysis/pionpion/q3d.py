#
# post_analysis/pionpion/q3d.py
#
"""
Module with classes and functions for dealing with the three dimentional
histograms containing Q_out Q_side Q_long particle data
"""

import numpy as np
import numpy.ma as ma
from itertools import starmap
from stumpy import Histogram


class Q3D:
    """
    Class wrapping a Q_{out,side,long} analysis - containing numerator and
    denominator histograms.
    """

    def __init__(self, numerator, denominator, do_sanity_check=True):
        self.num = Histogram.BuildFromRootHist(numerator)
        self.den = Histogram.BuildFromRootHist(denominator)

        ratio = numerator.Clone("ratio")
        ratio.Divide(denominator)
        self.ratio = Histogram.BuildFromRootHist(ratio)
        # self.ratio.errors = np.sqrt(self.ratio.data)

        assert self.num.shape == self.den.shape
        assert all(n[i] == d[i]
                   for n, d in zip(self.num.axes, self.den.axes)
                   for i in (2, 10, -2))


        if do_sanity_check:
            sanity_bins = self.num.get_slice((-.1, .1), (-.1, .1), (-.1, .1))
            sanity_data = np.array([
                self.num[x, y, z]
                for x in range(sanity_bins[0].start, sanity_bins[0].stop)
                for y in range(sanity_bins[1].start, sanity_bins[1].stop)
                for z in range(sanity_bins[2].start, sanity_bins[2].stop)
            ])
            # simple sanity test
            assert all(self.num[sanity_bins].flatten() == sanity_data)

        # store domain
        # ratio = self.num / self.den
        self.ratio_data = np.nan_to_num(self.ratio.data)  # self.num.data / self.den.data
        self.ratio_err = np.nan_to_num(self.ratio.errors)  # self.num.error / self.den.error
        #
        # self.ratio = np.nan_to_num(self.num / self.den)
        # self.ratio.data = self.ratio_data
        # # self.ratio.data = self.ratio_data
        #
        # self.ratio._ptr = numerator.Clone("_ptr")
        # self.ratio._ptr.Divide(numerator, denominator)
        self.num._ptr = numerator
        self.den._ptr = denominator
        self.ratio._ptr = ratio
        # print(self.ratio.data - self.ratio_data)
        assert (self.ratio.data == self.ratio_data).all(), "Error %f" % (np.max(self.ratio.data - self.ratio_data))

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
        slices = tuple(starmap(dom_to_slice, zip(self.num.axes, domain_tuples)))
        return slices

    def projection_out(self, y_domain=(-0.1, 0.1), z_domain=(-0.1, 0.1)):
        """
        Returns a numpy array of the entire 'out' axis, with the other two axes
        restricted by the parameters
        """
        # change domains into array slices
        # x_slice, y_slice, z_slice = self.bins_to_slices(
        #     y_domain=y_domain,
        #     z_domain=z_domain
        # )
        # x_slice = self.bins_to_slices
        #
        # num_slice = self.num[x_slice, y_slice, z_slice]
        # den_slice = self.den[x_slice, y_slice, z_slice]
        # self.get_projection()
        # data = num_slice / den_slice
        # # print("Sliced data", data.shape)
        # # print(data)
        # sum = data.sum(axis=(1, 2))

        data = self.ratio[:,y_domain,z_domain]
        sum = data.sum(axis=(1, 2))
        return sum

    def projection_side(self, x_domain=(-0.1, 0.1), z_domain=(-0.1, 0.1)):
        """
        Returns a numpy array of the entire 'side' axis, with the other two
        axes restricted by the parameters
        """
        data = self.ratio[x_domain,:,z_domain]
        sum = data.sum(axis=(0, 2))
        return sum

    def projection_long(self, x_domain=(-0.1, 0.1), y_domain=(-0.1, 0.1)):
        data = self.ratio[x_domain,y_domain,:]
        sum = data.sum(axis=(1, 2))
        return sum

    def get_projection(self, x_slice, y_slice, z_slice, summed_axes):
        """
        Returns a numpy array
        """
        data = self.data[x_slice, y_slice, z_slice]
        sum = data.sum(axis=summed_axes)
        return sum

    def projection_out_side(self, long_slice):
        # 2d projection x: out, y: side
        data = self.ratio.project_2d(0, 1, long_slice)
        return data

    def projection_out_long(self, side_slice):
        # 2d projection x: out, y: long
        data = self.ratio.project_2d(0, 2, long_slice)
        return data

    def projection_side_long(self, out_slice):
        # 2d projection x: side, y: long
        data = self.ratio.project_2d(1, 2, out_slice)
        return data

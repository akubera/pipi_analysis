#
# post_analysis/hist_helpers.py
#

import sys
from functools import partial

def coordinates_to_bin(hist, x, y=None, z=None):
    if y is None:
        return hist.getXAxis


def yes(hist):
    return True


def bin_range_1d(hist, x_min, x_max, inclusive_end=True):
    start = hist.FindBin(x_min)
    stop = hist.FindBin(x_max)
    if inclusive_end:
        stop += 1
    yield from range(start, stop)


def bin_range(hist, *,
              filter_zero_bins=True,
              exclude_flow_bins=True,
              x_range=None,
              y_range=None,
              z_range=None,
              x_bin_range=None,
              y_bin_range=None,
              z_bin_range=None):
    """
    Yields cartesian tripples for all points in histgoram. If provided, bins
    in any direction will be
    """

    def get_bin_range(axis, range_):
        return tuple(map(axis.FindBin, range_))

    def get_all_bins(axis):
        bin_count = axis.GetNbins()
        r = (1, bin_count + 1) if exclude_flow_bins else (0, bin_count + 2)
        return r

    def get_bins(real_range, bin_range, axis):
        if real_range is not None:
            return get_bin_range(axis, x_range)
        if bin_range is None:
            return get_all_bins(axis)
        return bin_range

    x_bin_range = get_bins(x_range, x_bin_range, hist.GetXaxis())
    y_bin_range = get_bins(y_range, y_bin_range, hist.GetYaxis())
    z_bin_range = get_bins(z_range, z_bin_range, hist.GetZaxis())

    for x in range(*x_bin_range):
        for y in range(*y_bin_range):
            for z in range(*z_bin_range):
                if filter_zero_bins and hist.GetBinContent(x, y, z) == 0:
                    continue
                yield x, y, z


def bin_centers(hist, bin_gen=None):
    if bin_gen is None:
        bin_gen = partial(bin_range)

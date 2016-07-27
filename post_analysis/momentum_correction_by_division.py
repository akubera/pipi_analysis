#!/usr/bin/env python
#
# momentum_correction_by_division.py
#
"""
Generate momentum corrections by
"""

import sys
import numpy as np
from stumpy import Histogram
from stumpy.utils import root_histogram_datatype
from argparse import ArgumentParser
from unittest.mock import MagicMock
from pionpion.femtolist import Femtolist
from pionpion.root_helpers import get_root_object
import ROOT

TRUE_NUM_PATH = ['CF_Num']
TRUE_DEN_PATH = ['CF_Den']


def parser():
    """
    Generate the argument parser.
    """
    parser = ArgumentParser("momentum_correction")
    parser.add_argument("filename", help="The ROOT file with data to read")
    parser.add_argument("--correction-file",
                        nargs='?',
                        default='MomentumCorrection.root',
                        help="ROOT file containing the momentum correction")
    parser.add_argument("--output",
                        nargs='?',
                        default=None,
                        help="Name of output file. If '-' no output is created")
    return parser


class Corrections:
    """
    A class wrapping the retrieval of MonteCarlo 'true' correlation
    functions. This is given a root file, and all numerator/denominator
    histogram pairs of montecarlo data are found and the corrections
    calculated.

    """

    def __init__(self, filename):
        """
        Args:
            filename (str): Filename of the correction file.
        """
        self.file = filename
        self._analyses = {}

    def __getitem__(self, analysis_name):
        """
        Return the normalized correction matrix for an analysis.
        """
        # get cached value
        try:
            return self._analyses[analysis_name]
        except KeyError:
            pass

        # load analysis
        try:
            analysis = self._femtolist[analysis_name]
        except KeyError:
            return None
        else:
            if analysis is None:
                return None

        def get_data_from_hist(root_hist):
            nbins = root_hist.GetNbinsX()
            dtype = root_histogram_datatype(root_hist)
            data = np.frombuffer(root_hist.GetArray(), dtype=dtype, count=nbins + 2)
            # ignore overflow+underflow bins
            return np.copy(data[1:-1])

        data = get_data_from_hist(self.make_ratio(*self.get_cf_hists(analysis._data)))

        result = self.Result()
        result.base = data
        result.kt_bins = {}

        if analysis.has_kt_bins():
            print("Momentum Correction analysis has kT bins")

            for b in analysis.kt_binned_pairs:
                bin_name = b.GetName()
                hists = self.get_cf_hists(b)
                print(hists)
                ratio = get_data_from_hist(self.make_ratio(*hists))
                result.kt_bins[bin_name] = ratio

        self._analyses[analysis_name] = result
        return result

    class Result:
        pass

    @staticmethod
    def get_cf_hists(obj):
        return (
            get_root_object(obj, ['NumTrueIdeal_MC_CF', 'ModelNumTrueIdeal', 'CF_Num']),
            get_root_object(obj, ['DenIdeal_MC_CF', 'ModelDenIdeal', 'CF_Den']),
            get_root_object(obj, ['NumTrue_MC_CF', 'ModelNumTrue', 'Num_qinv_pip']),
            get_root_object(obj, ['Den_MC_CF', 'ModelDen', 'Den_qinv_pip'])
        )

    @staticmethod
    def make_ratio(true_num, true_den, fake_num, fake_den):
        true_ratio = true_num.Clone()
        true_ratio.Divide(true_den)

        rec_ratio = fake_num.Clone()
        rec_ratio.Divide(fake_den)

        double_ratio = true_ratio.Clone()
        double_ratio.Divide(rec_ratio)
        return double_ratio

    @property
    def file(self):
        return self._file

    @file.setter
    def file(self, value):
        if isinstance(value, ROOT.TFile):
            self._file = value
        else:
            self._file = ROOT.TFile(value)
        self._femtolist = Femtolist(self._file)
        self._analyses = {}
        print("# Opened correction file:", value)

def take_hist_ratio(num, den, name="ratio", title="Ratio"):
    ratio = num.Clone(name)
    ratio.Divide(den)
    ratio.SetTitle(title)
    return ratio

def apply_correction_vector(root_hist_num, root_hist_den, norm_correction):
    num, den = root_hist_num, root_hist_den
    norm_dim_matches = num.GetNbinsX() == norm_correction.shape[0]
    num_den_dim_match = num.GetNbinsX() == den.GetNbinsX()

    if not num_den_dim_match:
        raise TypeError("Error: Numerator and Denominator do NOT match dimensions. Skipping.")

    elif not norm_dim_matches:
        a = norm_correction.shape[0]
        b = num.GetNbinsX()

        print("Warning: correction histogram has different shape than data, "
              "{} ≠ {}. Attempting rebin...".format(a, b),
              file=sys.stderr, end='')

        try:
            from math import gcd
        except ImportError: # python < 3.5 shim
            from fractions import gcd
        g = gcd(a, b)
        lcm = a * b / gcd(a, b)
        if not lcm or lcm % 1 != 0.0:
            raise ValueError("LCM could not be found. Skipping.")

        if a < b:
            scale = int(lcm // a)
            print("Rebinning by %s." % scale, file=sys.stderr)
            num.Rebin(scale)
            den.Rebin(scale)
        else:
            print("UNIMPLEMENTED... by %0.1f." % (lcm / a), file=sys.stderr)
            num.Rebin(a / lcm)
            den.Rebin(a / lcm)
            # norm_correction = norm_correction[::2] + norm_correction[1::2]

    root_ratio = take_hist_ratio(num, den, "cCF", "Corrected Correlation Function")
    for i, c in enumerate(norm_correction, 1):
        x = root_ratio.GetBinContent(i)
        e = root_ratio.GetBinError(i)
        root_ratio.SetBinContent(i, x * c)
        root_ratio.SetBinError(i, e * c)
    return root_ratio


def main(argv):
    # parse given argument list
    args = parser().parse_args(argv)

    # create output file
    if args.output is None:
        d = args.filename.rfind('.')
        output_filename = "%s.mcor%s" % (args.filename[:d], args.filename[d:])
        output = ROOT.TFile(output_filename, "RECREATE")
    elif args.output == '-':
        output = MagicMock()
    else:
        output = ROOT.TFile(args.output, "RECREATE")

    # load correction file
    corrections = Corrections(args.correction_file)

    # load data file
    femtolist = Femtolist(args.filename)

    # make output femtolist
    output_femtolist = output.mkdir(femtolist.name)

    # loop through analyses
    for analysis in femtolist:

        norm_correction = corrections[analysis.name]

        if norm_correction is None:
            print("No matching correction analysis %s. Skipping." % analysis.name)
            continue

        print("\n** Normalized Correction Data **")
        print(norm_correction.base)
        print()

        analysis_output = output_femtolist.mkdir(analysis.name)
        analysis_output.cd()

        num, den = analysis[analysis.QINV_NUM_PATH], analysis[analysis.QINV_DEN_PATH]

        basecf = take_hist_ratio(num, den, "CF", "(UnCorrected) Correlation Function")
        basecf.Write()


        try:
            root_ratio = apply_correction_vector(num, den, norm_correction.base)
        except Exception as err:
            print(err, file=sys.stderr)
            output_femtolist.rmdir(analysis.name)
            continue

        root_ratio.Write()

        for kt_data in analysis.kt_binned_pairs:
            bin_name = kt_data.GetName()
            # ROOT.TDirectory.Cd(analysis.name)
            path = "%s/%s/" % (analysis.KT_BINNED_ANALYSIS_PATH[0], bin_name)
            analysis_output.mkdir(path).cd()
            # analysis_output.mkdir()
            try:
                correction = norm_correction.kt_bins[bin_name]
            except KeyError:
                print("No kt_bin '%s' in correction file" % bin_name, file=sys.stderr)
                continue

            num = get_root_object(kt_data, analysis.QINV_NUM_PATH)
            den = get_root_object(kt_data, analysis.QINV_DEN_PATH)
            analysis_output.cd(path)
            cCF = apply_correction_vector(num, den, correction)
            cf = take_hist_ratio(num, den, "CF", "(UnCorrected) Correlation Function")
            cf.Write()
            cCF.Write()

    output.Close()

if __name__ == "__main__":
    main(sys.argv[1:])

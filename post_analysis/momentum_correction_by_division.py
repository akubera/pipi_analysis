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
    A class wrapping the retrieval of MonteCarlo 'true' correlation functions.
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
            print("XXX")
            return None
        else:
            print("YYY")
            if analysis is None:
                print("ZZZ")
                return None

        # load 'true' correlation functions from analysis
        true_num = analysis[TRUE_NUM_PATH]
        true_den = analysis[TRUE_DEN_PATH]
        print(true_num, true_den)

        rec_num = analysis[analysis.QINV_NUM_PATH]
        rec_den = analysis[analysis.QINV_DEN_PATH]
        print(rec_num, rec_den)

        true_ratio = true_num.Clone()
        rec_ratio = rec_num.Clone()

        true_ratio.Divide(true_den)
        rec_ratio.Divide(rec_den)

        double_ratio = true_ratio.Clone()
        double_ratio.Divide(rec_ratio)

        # true_ratio.Draw()
        # input()
        # rec_ratio.Draw()
        # input()
        # double_ratio.Draw()
        # input()

        nbins = double_ratio.GetNbinsX()
        dtype = root_histogram_datatype(double_ratio)
        data = np.frombuffer(double_ratio.GetArray(), dtype=dtype, count=nbins + 2)

        # ignore overflow+underflow bins
        data = np.copy(data[1:-1])
        self._analyses[analysis_name] = data

        return data

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
        try:
            norm_correction = corrections[analysis.name]
        except IndexError:
            print("No matching correction analysis %s. Skipping." % analysis.name)
            continue
        print("\n** Normalized Correction Data **")
        print(norm_correction)
        print()

        # num, den = analysis.qinv_pair
        num, den = analysis[analysis.QINV_NUM_PATH], analysis[analysis.QINV_DEN_PATH]

        # if num.GetXaxis().GetXmax() != norm_correction.
        if num.GetNbinsX() != norm_correction.shape[0]:
            factor = num.GetNbinsX() // norm_correction.shape[0]
            num = num.Rebin(factor)

        if den.GetNbinsX() != norm_correction.shape[0]:
            factor = den.GetNbinsX() // norm_correction.shape[0]
            den = den.Rebin(factor)
            # if (num.GetNbinsX() / norm_correction.shape) % 1 == 0.0:


        num, den = Histogram.BuildFromRootHist(num), Histogram.BuildFromRootHist(den)
        ratio = num / den
        print('ratio', num.shape, den.shape, norm_correction.shape)
        corrected_ratio = ratio * norm_correction

        print("\n** Corrected CF **")
        print(ratio)
        print()

        # import matplotlib.pyplot as plt
        # plt.plot(ratio.data[:30])
        # plt.plot(corrected_ratio.data[:30])
        # plt.show()

        # this applies the matrix to ALL qinv histograms
        # analysis.apply_momentum_correction(norm_correction)

        # write the smeared output
        analysis.write_into(output_femtolist)

    output.Close()

if __name__ == "__main__":
    main(sys.argv[1:])

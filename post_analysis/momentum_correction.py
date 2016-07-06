#!/usr/bin/env python
#
# momentum_correction.py
#

import sys
import numpy as np
from stumpy import Histogram
from argparse import ArgumentParser
from unittest.mock import MagicMock
from pionpion.femtolist import Femtolist
import ROOT


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
    parser.add_argument("--correction-hist-path",
                        nargs='?',
                        default='Pair.pass.mc_Qinv',
                        help="Per-analysis path of correction histogram")
    parser.add_argument("--output",
                        nargs='?',
                        default=None,
                        help="Name of output file. If '-' no output is created")
    return parser


class Corrections:
    """
    A class wrapping the retrieval of momentum correction matrixes.
    """

    def __init__(self, filename, hist_path):
        """
        Args:
            filename (str): Filename of the correction file.
            hist_path (str): The common path to the 2D histogram found
                in the root file.
        """
        self.file = filename
        self._hist_path = hist_path

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

        # load correction histogram from analysis
        root_correction = analysis[self._hist_path]
        if root_correction is None:
            print("Could not find correction histogram", self._hist_path, "in", analysis_name)
            return None
        else:
            correction = Histogram.BuildFromRootHist(root_correction)

        # normalize the correction matrix
        norm_correction = self.normalize_correction_hist_true(correction)
        # norm_correction = self.normalize_correction_hist_rec(correction)
        # norm_correction = self.normalize_correction_hist_both(correction)


        # cache and return result
        self._analyses[analysis_name] = norm_correction
        return norm_correction

        norm = correction.data / norm_factor_0

    @staticmethod
    def normalize_correction_hist_true(correction):
        """
        Normalize a 2D Histogram (behaving as a matrix)
        Args:
            correction: Square 2D histogram with
        """
        # normalize so q_true (rows) sum to 1.0
        norm_factor = correction.data.sum(axis=0, keepdims=True, dtype=float)
        norm = correction.data / norm_factor
        return norm

    @staticmethod
    def normalize_correction_hist_rec(correction):
        """
        Normalize a 2D Histogram (behaving as a matrix)
        Args:
            correction: Square 2D histogram with
        """
        # normalize so q_rec (columns) sum to 1.0
        norm_factor = correction.data.sum(axis=1, keepdims=True, dtype=float)
        norm = correction.data / norm_factor
        return norm

    @staticmethod
    def normalize_correction_hist_both(correction):
        # normalize along q_true
        norm_factor_true = correction.data.sum(axis=0, keepdims=True, dtype=float)

        true_norm = correction.data / norm_factor_true

        # normalize along q_rec
        norm_factor_reconstructed = true_norm.sum(axis=1, keepdims=True)

        return true_norm / norm_factor_reconstructed

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
    args = parser().parse_args(argv)

    if args.output is None:
        d = args.filename.rfind('.')
        output_filename = "%s.mcor%s" % (args.filename[:d], args.filename[d:])
        output = ROOT.TFile(output_filename, "RECREATE")
    elif args.output == '-':
        output = MagicMock()
    else:
        output = ROOT.TFile(args.output, "RECREATE")

    # load correction file
    corrections = Corrections(args.correction_file, args.correction_hist_path)

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

        # this applies the matrix to ALL qinv histograms
        analysis.apply_momentum_correction(norm_correction)

        # write the smeared output
        analysis.write_into(output_femtolist)

    output.Close()

if __name__ == "__main__":
    main(sys.argv[1:])

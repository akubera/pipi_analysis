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
    correction_file = ROOT.TFile(args.correction_file)
    correction_file_femtolist = Femtolist(correction_file)
    print("# Found correction file:", correction_file)

    # load data file
    femtolist = Femtolist(args.filename)

    output_femtolist = output.mkdir(femtolist.name)

    # loop through analyses
    for analysis in femtolist:
        try:
            correction_analysis = correction_file_femtolist[analysis.name]
        except IndexError:
            print("No matching correction analysis %s. Skipping." % analysis.name)
            continue

        print('>', correction_analysis)
        correction = correction_analysis[args.correction_hist_path]
        if correction == None:
            print("No correction path ", args.correction_hist_path)
            continue
        correction = Histogram.BuildFromRootHist(correction)
        norm_factor = correction.data.sum(axis=1, keepdims=True, dtype=float)

        # normalization matrix
        norm = correction.data / norm_factor

        # this applies the matrix to ALL qinv histograms
        analysis.apply_momentum_correction(norm)

        # write the smeared output
        analysis.write_into(output_femtolist)

    output.Close()

if __name__ == "__main__":
    main(sys.argv[1:])

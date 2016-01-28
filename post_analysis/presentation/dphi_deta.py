#!/usr/bin/env python3.4
#
# post_analysis/presentation/dphi_deta.py
#
"""
Script which loops through femtolist and prints the configuration of each
analysis.
"""
import sys
from argparse import ArgumentParser
from pionpion import Femtolist
import ROOT

parser = ArgumentParser()
parser.add_argument("--title-suffix",
                    type=str,
                    nargs='?',
                    default='',
                    help="Adds the words to the end of the histogram title")
parser.add_argument("root_filename", help="root filename to analyze")
parser.add_argument("output_filename", help="root filename to analyze")
args = parser.parse_args()

NUM_PATH = (
    'NumDPhiStarDEta_dphi_deta',
)

DEN_PATH = (
    'DenDPhiStarDEta_dphi_deta',
)

for analysis in Femtolist(args.root_filename):
    num = analysis[NUM_PATH]
    den = analysis[DEN_PATH]

    if num == None or den == None:
        print(analysis.GetName(), "Could not find numerator or denominator objects", file=sys.stderr)
        continue

    ratio = num.Clone("ratio")
    ratio.Divide(den)
    ratio.Draw("colz")

    ROOT.gApplication.Run()

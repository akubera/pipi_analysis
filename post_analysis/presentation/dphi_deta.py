#!/usr/bin/env python3.4
#
# post_analysis/presentation/dphi_deta.py
#
"""
Script which loops through femtolist and prints the configuration of each
analysis.
"""
import sys
import lmfit
from pionpion.femtolist import Femtolist
from argparse import ArgumentParser
import ROOT

parser = ArgumentParser()
parser.add_argument("--title-suffix",
                    type=str,
                    nargs='?',
                    default='',
                    help="Adds the words to the end of the histogram title")
parser.add_argument("root_filename",
                    help="root filename to analyze")
parser.add_argument("output_filename",
                    default=None,
                    help="root filename to analyze, use '-' to indicate no output")
args = parser.parse_args()

NUM_PATH = (
    'NumDPhiStarDEta_d',
    'NumDPhiStarDEta_',
)

DEN_PATH = (
    'DenDPhiStarDEta_d',
    'DenDPhiStarDEta_',
)

if args.output_filename != "-":
    ofile = ROOT.TFile(args.output_filename, "RECREATE")
else:
    ofile = None

def make_output_analysis(name):
    if ofile is None:
        from unittest.mock import Mock
        return Mock()
    return ofile.mkdir(name)

for analysis in Femtolist(args.root_filename):
    num = analysis[NUM_PATH]
    den = analysis[DEN_PATH]

    if num == None or den == None:
        print(analysis.name,
              "Could not find numerator or denominator objects",
              file=sys.stderr)
        continue



    output = make_output_analysis(analysis.name)

    ratio = num.Clone("ratio")
    ratio.Divide(den)
    ratio.Draw("colz")
    ratio.SetTitle("#Delta#eta vs #Delta#phi* - RATIO; #Delta#eta; #Delta#phi*")
    ratio.SetStats(False)

    output.WriteTObject(num, "numerator")
    output.WriteTObject(den, "denominator")
    output.WriteTObject(ratio)

    x = ratio.ProjectionX()
    x.SetTitle("#Delta#eta")
    output.WriteTObject(x, "delta_eta")
    x = ratio.ProjectionY()
    x.SetTitle("#Delta#phi*")
    output.WriteTObject(x, "delta_phi")

    # input()

if ofile:
    ofile.Write()

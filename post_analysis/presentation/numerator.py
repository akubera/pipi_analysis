#!/usr/bin/env python3.4
#
# post_analysis/presentation/numerator.py
#
"""
Script which loops through femtolist and prints the configuration of each
analysis.
"""

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

QINV_NUMERATOR = (
    "Num_qinv_pip",
    "Num_qinv_pim",
)

for analysis in Femtolist(args.root_filename):
    numerator = analysis[QINV_NUMERATOR]
    if numerator == None:
        print("No numerator found in", analysis)
        continue
    title = "%s Q_{inv} Numerator %s;" % (analysis.system_name, args.title_suffix)
    title = title.replace("π", "#pi")
    numerator.SetTitle(title + "q_{inv}; N_{pairs};")
    numerator.GetYaxis().SetTitleOffset(1.25)
    canvas = ROOT.TCanvas("canvas")
    numerator.Draw()
    canvas.SaveAs(args.output_filename)
    break

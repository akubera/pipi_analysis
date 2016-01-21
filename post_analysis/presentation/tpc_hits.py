#!/usr/bin/env python3.4
#
# post_analysis/presentation/numerator.py
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

CHI_TPC_ITS_PASS = (
    "Tracks.pass.ChiTpcIts",
)
CHI_TPC_ITS_FAIL = (
    "Tracks.fail.ChiTpcIts",
)

for analysis in Femtolist(args.root_filename):
    tpc_its_pass = analysis[CHI_TPC_ITS_PASS]
    tpc_its_fail = analysis[CHI_TPC_ITS_FAIL]

    if tpc_its_pass == None or tpc_its_fail == None:
        print(analysis.GetName(), "Could not find any objects named 'ChiTpcIts'", file=sys.stderr)
        continue

    a = ROOT.TCanvas("a")
    tpc_its = tpc_its_pass.Clone("tpc_its")
    tpc_its.Add(tpc_its_fail)
    tpc_its.Draw()

    b = ROOT.TCanvas("b")
    tpc_projection = tpc_its.ProjectionX("tpc_n_sigma")
    tpc_projection.SetTitle("#pi^{+}  N_{#sigma, TPC}; #chi^{2} / N_{cls} TPC; N_{tracks}")
    tpc_projection.GetYaxis().SetTitleOffset(1.25)
    tpc_projection.Draw("-")
    input()

    break

    if numerator == None:
        print("No numerator found in", analysis)
        continue
    title = "%s Q_{inv} Numerator %s;" % (analysis.system_name, args.title_suffix)
    title = title.replace("π", "#pi")
    numerator.SetTitle(title + "q_{inv}; N_{pairs};")
    numerator.GetYaxis().SetTitleOffset(1.25)
    numerator.SetFillStyle(4000)
    canvas = ROOT.TCanvas("canvas")
    canvas.SetFrameFillColor(4000)
    canvas.SetFillStyle(4000)
    numerator.Draw()
    canvas.SaveAs(args.output_filename)

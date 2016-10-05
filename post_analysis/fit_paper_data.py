#!/usr/bin/env python
#
# fit_paper_data.py
#

import sys
from pathlib import Path
from argparse import ArgumentParser
from pionpion.root_helpers import get_root_object
from fitting.gaussian import GaussianModelCoulomb, GaussianModelFSI
from uncorrected_ktbinned_qinv_fit import do_qinv_fit, fitres_to_tgraph
from lmfit import report_fit
# import numpy as np
import ROOT

parser = ArgumentParser("fit_paper_data")
parser.add_argument("--paper-root-file",
                    nargs='?',
                    # default='../paper-pion-data/PionsCF.root',
                    default='paper-pion-data/FigAdd_PionCF.root',
                    help="Path to the pion data")
parser.add_argument("--fit-range",
                    nargs='?',
                    default='0:0.06',
                    help="Range of fit")

args = parser.parse_args()

paper_data = ROOT.TFile(args.paper_root_file, "READ")
if not paper_data:
    print("Could not open paper-data root file", file=sys.stderr)
    sys.exit(1)

fit_range = tuple(map(eval, args.fit_range.split(':')))

hist = get_root_object(paper_data, '') # "RatcqinvpiptpcmrM1kT1")

if not isinstance(hist, ROOT.TH1):
    print("Histogram with expected name RatcqinvpiptpcmrM1kT1 not found in %s" %
          args.paper_root_file,
          file=sys.stderr)
    sys.exit(1)

my_data = ROOT.TFile('data/16/09/30/pipi.kt_qinv.root', "READ")
my_analysis = get_root_object(my_data, 'PiPiAnalysis_00_10_pip')
for x in my_analysis.GetListOfKeys():
    if x.GetName() == "0.300_0.400":
        my_kt_bin = x.ReadObj()
        break
else:
    print("Could not find kt bin")
    sys.exit(1)
print(my_kt_bin)
my_hist = get_root_object(my_kt_bin, "cf_normalized")

FIT_CLASS = GaussianModelCoulomb
FIT_CLASS = GaussianModelFSI

fit = do_qinv_fit(hist, FIT_CLASS, fit_range)
report_fit(fit)
graph = fitres_to_tgraph(fit)
leg = ROOT.TLegend(0.7,0.7,0.9,0.9)
# leg.SetHeader("Comparison","C") # option "C" allows to center the header
leg.AddEntry(hist, "PaperData", "lep")
leg.AddEntry(my_hist, "MyData", "lep")
hist.SetTitle("CF : 0-10% Centrality : 0.3-0.4 GeV k_{T}")
hist.SetStats(False)
hist.GetXaxis().SetRangeUser(0.0, 0.1)
hist.Draw()
graph.Draw("same")
my_hist.Draw("same")
leg.Draw()
input()
# model = FIT_CLASS()
# model.eval(fit.params)

#!/usr/bin/env python3
#
# post_analysis/minuit_fit.py
#

import sys
import numpy as np
from argparse import ArgumentParser
from fit_params import (
    FitParam,
    fit_params,
)
from pionpion.root_helpers import get_root_object
from ROOT import TFile
from ROOT import TMinuit


parser = ArgumentParser()
parser.add_argument("filename", help="root filename to analyze")
args = parser.parse_args()

file = TFile(args.filename, 'READ')

femtolist = get_root_object(file, ['femtolist', 'PWG2FEMTO.femtolist'])

if femtolist == None:
    print("Could not find femtolist", file=sys.stderr)
    sys.exit(1)

num = femtolist.FindObject("Numcqinv_pip_tpcM0")
den = femtolist.FindObject("Dencqinv_pip_tpcM0")

fit_range = 0.4, 0.7

num_scale = 1.0 / num.Integral(*map(num.FindBin, fit_range))
den_scale = 1.0 / den.Integral(*map(den.FindBin, fit_range))


ratio = num.Clone("ratio")
ratio.Divide(num, den, num_scale, den_scale)
ratio.SetTitle(r"#pi^{+} CF; q_{inv} (GeV); C(q_{inv})")
ratio.GetXaxis().SetRangeUser(0, 0.5)
# ratio.Draw()

fitter = TMinuit()

for i, param in enumerate(fit_params):
    fitter.DefineParameter(i, param.name, param.ival)
    # fitter.DefineParameter(iPar, fMinuitParNames[iPar], fMinuitParInitial[iPar], startingStepSize, fMinuitParMinimum[iPar], fMinuitParMaximum[iPar]);
print(fitter)

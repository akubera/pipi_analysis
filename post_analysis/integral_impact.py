#!/usr/bin/env python3
#
# post_analysis/integral_impact.py
#

import sys
import math
import time
import numpy as np
from argparse import ArgumentParser
from itertools import starmap as apply
from functools import partial
from collections import defaultdict
import numbers
from fit_params import (
    FitParam,
    fit_params,
)
from lmfit import minimize, Parameters, report_fit
import ROOT
from ROOT import (
    TFile,
    TMinuit,
)
import pionpion
from pionpion.root_helpers import get_root_object


parser = ArgumentParser()
parser.add_argument("filename", help="root filename to analyze")
# parser.add_argument("output",
#                     nargs='?',
#                     default='Result.root',
#                     help="root filename to analyze")
args = parser.parse_args()

file = TFile(args.filename, 'READ')

femtolist = pionpion.Femtolist(file)

for analysis in femtolist:

    analysis_name = analysis.GetName()
    impact = analysis['Tracks.pass.impact']
    xs = tuple(map(impact.GetXaxis().FindBin, (-3.0, 3.0)))
    ys = tuple(map(impact.GetYaxis().FindBin, (0, 2.5)))

    sum = impact.Integral(xs[0], ys[1], *ys)
    print("Integral[impact] =", sum)


    for end in (0.1, 0.15, 0.2, 0.25, 0.3, 0.35, 0.4, 0.5, 0.6 ,0.7 ,0.8, 0.9):
        ys = tuple(map(impact.GetYaxis().FindBin, (0.0, end)))
        slim = impact.Integral(xs[0], ys[1], *ys)
        print("Integral(impact[%.03f]) = %f" % (end, slim))
        print(" > %f" % (slim/sum))

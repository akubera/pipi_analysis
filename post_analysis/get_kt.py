#!/usr/bin/env python3
#
# post_analysis/get_kt.py
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
parser.add_argument("output",
                    nargs='?',
                    default='Result.root',
                    help="root filename to analyze")
args = parser.parse_args()

file = TFile(args.filename, 'READ')

femtolist = pionpion.Femtolist(file)

output = TFile(args.output, 'RECREATE')


for analysis in femtolist:

    analysis_name = analysis.GetName()

    output.mkdir(analysis_name)
    output.cd(analysis_name)

    kt = analysis["Pair.pass.kt"]
    if kt == None:
        continue

    kt.Write()

output.Write()
output.Close()

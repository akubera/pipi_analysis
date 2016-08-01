#!/usr/bin/env python3
#
# post_analysis/qinv_fit.py
#

import sys
import time
import pionpion
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from pprint import pprint
from argparse import ArgumentParser, Action
from pionpion import Femtolist
from pionpion.analysis import Analysis
from pionpion.fit import fitfunc_qinv
from pionpion.fit import fitfunc_qinv_gauss_ll
from fitting.gaussian import GaussianModelCoulomb, GaussianModelFSI
from lmfit import minimize, Parameters, report_fit
from pionpion.root_helpers import get_root_object
from stumpy import Histogram

import ROOT


def argument_parser():
    parser = ArgumentParser('qinv_fit.py')
    parser.add_argument("--fit-range",
                        nargs='?',
                        default='0:0.16',
                        help="Range of normalization")
    parser.add_argument("--output-domain",
                        nargs='?',
                        default='0.0:0.5',
                        help="Output plot?")
    parser.add_argument("--title-suffix",
                        type=str,
                        nargs='?',
                        default='',
                        help="Adds the words to the end of the histogram title")
    parser.add_argument("--use-ll",
                        action='store_true',
                        help="Uses the log-likelihood fitting procedure")
    parser.add_argument("datafile", help="ROOT filename to analyze")
    parser.add_argument("output_filename",
                        nargs='?',
                        default=None,
                        help="Output root filename to store results")
    return parser


def do_qinv_fit(ratio, ModelClass, fit_range):
    """
    Do a fit of numerator denominator pairs.
    """
    # ratio = num / den
    qinv_params = ModelClass.guess(ratio)
    fit_slice = ratio.x_axis.get_slice(fit_range)

    y = ratio.data[fit_slice]
    nonzero_mask = y != 0

    x = ratio.x_axis.bin_centers[fit_slice][nonzero_mask]
    y = y[nonzero_mask]
    e = ratio.errors[fit_slice][nonzero_mask]
    # print('y', y)
    # print('e', e)
    qinv_fit = minimize(ModelClass.as_resid, qinv_params, args=(x, y, e))

    return qinv_fit


def plot_cf_and_fit(cf, fit_res, ModelClass=GaussianModelFSI):
    """
    Plot a correlation with line of best fit as determined by some
    fit results.
    """
    if isinstance(cf, Histogram):
        cf = cf.AsRootHist()

    FIT_X = np.linspace(0.0, 0.16, 300)
    FIT_Y = ModelClass().eval(fit_res.params, x=FIT_X)
    cf.GetXaxis().SetRangeUser(0, 0.3)
    cf.Draw()
    fit_plot = ROOT.TGraph(len(FIT_X), FIT_X, FIT_Y)
    fit_plot.SetLineColor(2)
    fit_plot.Draw("Same")

    input()


def main(argv):

    args = argument_parser().parse_args(argv)

    if args.use_ll:
        print("LogLikelihood not implemented for kT-binned fit! Aborting.", file=sys.stderr)
        return

    # create the femtolist from the input file
    femtolist = Femtolist(args.datafile)

    # no exception means femtolist is good - create outputfile
    if args.output_filename is None:
        basename, _, ext = args.datafile.rpartition('.')
        args.output_filename = basename + ".kt_qinv." + ext

    output_file = ROOT.TFile(args.output_filename, 'RECREATE')
    fit_range = args.fit_range.split(':')
    FIT_CLASS = GaussianModelFSI

    for analysis in femtolist:
        print("\n***", analysis.name)
        kt_analysis = analysis['KT_Qinv']

        root_cf = analysis['CF']
        cf = Histogram.BuildFromRootHist(root_cf)
        cf_fit_res = do_qinv_fit(cf, FIT_CLASS, (0, 0.16))

        report_fit(cf_fit_res)

        plot_cf_and_fit(root_cf, cf_fit_res)

        for x in list(map(ROOT.TKey.ReadObj, kt_analysis.GetListOfKeys())):
            root_cf = get_root_object(x, 'CF')
            root_ccf = get_root_object(x, 'cCF')

            cf = Histogram.BuildFromRootHist(root_cf)
            corrected_cf = Histogram.BuildFromRootHist(root_ccf)

            cf_fit_res = do_qinv_fit(cf, FIT_CLASS, (0, 0.16))
            corrected_fit_res = do_qinv_fit(corrected_cf, FIT_CLASS, (0, 0.16))

            # pd.DataFrame()
            # print(res.valuesdict())
            print()
            print()
            report_fit(corrected_fit_res)
            plot_cf_and_fit(root_ccf, corrected_fit_res)
            # print(dict(**cf_fit_res.params))

    output_file.Close()


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))

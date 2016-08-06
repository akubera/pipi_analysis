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

from copy import copy
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
    parser.add_argument('-b', "--batch",
                        action='store_true',
                        help="Run in batch mode (no plots draw)")
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


def fitres_to_tgraph(fit_res, domain=(0.0, 0.16), npoints=300, ModelClass=GaussianModelFSI):
    FIT_X = np.linspace(*domain, num=300)
    FIT_Y = ModelClass().eval(fit_res.params, x=FIT_X)
    # FIT_Y = GaussianModelFSI.gauss(FIT_X, normalized=True, **fit_res.params)
    return ROOT.TGraph(len(FIT_X), FIT_X, FIT_Y)


def plot_cf_and_fit(cf, fit_res, ModelClass=GaussianModelFSI, canvas=None):
    """
    Plot a correlation with line of best fit as determined by some
    fit results.d
    """
    if isinstance(cf, Histogram):
        cf = cf.AsRootHist()

    cf.GetXaxis().SetRangeUser(0, 0.3)
    cf.Draw()
    fit_plot = fitres_to_tgraph(fit_res)
    fit_plot.SetLineColor(2)
    # fit_plot.SetTitle("")
    fit_plot.Draw("Same")
    return fit_plot


def save_fit_canvas(root_cf, fit_res, name, normalized=True):
    """
    Create a canvas
    """
    root_cf.SetStats(False)

    if normalized:
        fit_res = copy(fit_res)
        fit_res.params['norm'].value = 1.0

    canvas = ROOT.TCanvas('www')
    canvas.cd()
    root_cf.GetXaxis().SetRangeUser(0.0, 0.3)
    root_cf.GetYaxis().SetRangeUser(0.88, 1.25)
    fit_plot = fitres_to_tgraph(fit_res)

    txt = ROOT.TPaveText(0.6, 0.7, 0.87, 0.87, "NDCL")
    txt.AddText("#lambda %f" % fit_res.params['lam'] )
    txt.AddText("R_{inv} %f" % fit_res.params['radius'] )
    root_cf.Draw()
    fit_plot.Draw("same")
    txt.Draw()

    canvas.Write(name)

    return canvas

def main(argv):

    args = argument_parser().parse_args(argv)

    if args.use_ll:
        print("LogLikelihood not implemented for kT-binned fit! Aborting.", file=sys.stderr)
        return

    if args.batch:
        print("-- Running in batch mode")
        ROOT.gROOT.SetBatch(True)

    # create the femtolist from the input file
    femtolist = Femtolist(args.datafile)

    # no exception means femtolist is good - create outputfile
    if args.output_filename is None:
        basename, _, ext = args.datafile.rpartition('.')
        args.output_filename = basename + ".kt_qinv." + ext

    output_file = ROOT.TFile(args.output_filename, 'RECREATE')
    fit_range = args.fit_range.split(':')
    FIT_CLASS = GaussianModelFSI

    def write_fit(root_cf, title, name):
        root_cf.SetTitle(title)
        cf = Histogram.BuildFromRootHist(root_cf)
        cf_fit_res = do_qinv_fit(cf, FIT_CLASS, (0, 0.16))
        root_cf.Scale(1.0 / cf_fit_res.params['norm'])
        report_fit(cf_fit_res)
        save_fit_canvas(root_cf, cf_fit_res, name)

    for analysis in femtolist:
        print("\n***", analysis.name)

        # Set output for this analysis
        output_dir = output_file.mkdir(analysis.name)
        output_dir.cd()

        # Get the correlation function
        write_fit(analysis['CF'],
                  name='CF_fit',
                  title="(Uncorrected) CF : %s" % (analysis.title))
        
        write_fit(analysis['cCF'],
                  name='cCF_fit',
                  title="(Corrected) CF : %s" % (analysis.title))

        try:
            kt_analysis = analysis['KT_Qinv']
        except KeyError:
            print("-- No KT bins found for %s." % analysis.name)
            continue

        
        kt_bins = tuple((x.GetName(), x.ReadObj()) for x in kt_analysis.GetListOfKeys())

        for name, x in kt_bins:
            output_dir.mkdir(name).cd()

            write_fit(get_root_object(x, 'CF'),
                      name='CF_fit',
                      title="(Uncorrected) CF : %s" % (analysis.title))
        
            write_fit(get_root_object(x, 'cCF'),
                      name='cCF_fit',
                      title="(Corrected) CF : %s" % (analysis.title))

    output_file.Close()


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))

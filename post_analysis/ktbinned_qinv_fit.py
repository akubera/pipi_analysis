#!/usr/bin/env python3
#
# post_analysis/qinv_fit.py
#

import sys
import time
import pionpion
import numpy as np
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


def do_qinv_fit(num, den, ModelClass, fit_range, use_loglikely=True):
    """
    Do a fit of numerator denominator pairs.
    """
    ratio = num / den
    qinv_params = ModelClass.guess(ratio)
    fit_slice = ratio.x_axis.get_slice(FIT_RANGE)
    x = ratio.x_axis.bin_centers[fit_slice]

    if use_loglikely:
        qinv_fit = minimize(ModelClass.as_loglike, qinv_params, args=(x, num[fit_slice], den[fit_slice]))
    else:
        y = ratio.data[fit_slice]
        e = ratio.errors[fit_slice]
        qinv_fit = minimize(ModelClass.as_resid, qinv_params, args=(x, y, e))

    return qinv_fit


def main(argv):

    args = argument_parser().parse_args(argv)

    # create the femtolist from the input file
    femtolist = Femtolist(args.datafile)

    # no exception means femtolist is good - create outputfile
    if args.output_filename is None:
        ext_position = args.datafile.rfind('.')
        args.output_filename = args.datafile[:ext_position] + ".kt_qinv" + args.datafile[ext_position:]

    output_file = ROOT.TFile(args.output_filename, 'RECREATE')
    fit_range = args.fit_range.split(':')
    FIT_CLASS = GaussianModelFSI

    for analysis in femtolist:
        print("***", analysis.name)
        kt_analysis = analysis['KT_Qinv']

        if not kt_analysis:
            print("No Kt Analysis found")
            continue

        # for kt_bin in kt_analysis:
        for kt_bin in analysis.kt_binned_pairs:
            print(kt_bin)
            name = kt_bin.GetName()
            num = Histogram.BuildFromRootHist(get_root_object(kt_bin, Analysis.QINV_NUM_PATH))
            den = Histogram.BuildFromRootHist(get_root_object(kt_bin, Analysis.QINV_DEN_PATH))

            fit_res = do_qinv_fit(num, den, FIT_CLASS)
            report_fit(fit_res, show_correl=False)

            x = np.linspace(0, 1.0, 300)
            y = FIT_CLASS.gauss(x, **fit_res.params)
            plot = ROOT.TGraph(len(x), x, y)
            plot.Write()
            # plt.plot(x, y)
            # plt.show()
            input()
            continue

            print("\n:::Chi-Squared Fit:::::")
            # norm_ratio = num / np.sum(num[0.7:0.8]) / (den / np.sum(den[0.7:0.8]))
            norm_ratio = num / den


            qinv_params = Parameters()
            qinv_params.add('radius', value=6.5, min=0.0)
            qinv_params.add('lam', value=0.5)  # , min=0.0, max=1.0)
            qinv_params.add('norm', value=1.0)  # , min=0.0, max=1.0)

            fit_method = 'leastsq'

            b = norm_ratio.bin_at(0.2)
            # b = 28
            print('b:',b)
            fit_args = num.x_axis.bin_centers[:b], (norm_ratio.data[:b], norm_ratio.errors[:b])

            tfit = minimize(fitfunc_qinv, qinv_params, args=fit_args, method=fit_method)

            fitx = np.linspace(0, 0.1, 100)
            fity = fitfunc_qinv(tfit.params, fitx)
            report_fit(tfit)
            print("\n:::LL-Fit:::::")

            qinv_params = Parameters()
            # qinv_params.add('radius', value=tfit.params['radius'].value, min=0.0)
            # qinv_params.add('lam', value=tfit.params['lam'].value)
            qinv_params.add('radius', value=6.5, min=0.0)
            qinv_params.add('lam', value=0.5)
            qinv_params.add('norm', value=1)



            fit_args = (num.x_axis.bin_centers[:b], (num.data[:b], den.data[:b]))

            # print("    ::"),
            # pprint(list(zip(fit_args[0], *fit_args[1])))

            TIMESTART = time.monotonic()
            qinv_fit = minimize(fitfunc_qinv_gauss_ll, qinv_params, args=fit_args, method=fit_method)
            TIME_DELTA = time.monotonic() - TIMESTART
            time_per_call = TIME_DELTA * 1e3 / qinv_fit.nfev
            report_fit(qinv_fit)
            print("fitting time %0.3fs (%0.3f ms/call)" % (TIME_DELTA, time_per_call))

            fitll = fitfunc_qinv(qinv_fit.params, fitx)
            plt.plot(fitx, fity, 'r-',
                     fitx, fitll, 'g-',)

            plt.errorbar(norm_ratio.x_axis.bin_centers[:b],
                         norm_ratio.data[:b],
                         yerr=norm_ratio.errors[:b],
                         fmt='b.',
                         )
            plt.title = name
            plt.show()

    output_file.Close()


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))

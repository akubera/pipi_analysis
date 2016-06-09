#!/usr/bin/env python3
#
# post_analysis/qinv_fit.py
#
"""
Performs a 1D (qinv) fit from all qinv correlation histograms in datafile.
"""

import sys
import time
import pionpion
import numpy as np
import matplotlib.pyplot as plt

from pprint import pprint
from unittest.mock import MagicMock
from argparse import ArgumentParser, Action
from lmfit import minimize, Parameters, report_fit
from rootpy.interactive import wait

from pionpion import Femtolist
from pionpion.fit import fitfunc_qinv, fitfunc_qinv_gauss_ll
from post_analysis.fitting.gaussian import (
    GaussianModel,
    GaussianModelCoulomb,
    GaussianModelFSI,
)

import ROOT  # import root last


def argument_parser():
    parser = ArgumentParser('qinv_fit.py')
    parser.add_argument("--fit-max",
                        type=float,
                        nargs='?',
                        default=0.16,
                        help="Maximum qinv value of the fit range")
    parser.add_argument("--norm-range",
                        nargs='?',
                        default='0.8:1.1',
                        help="Range of normalization")
    parser.add_argument("--output-domain",
                        nargs='?',
                        default='0.0:0.5',
                        help="Range of normalization")
    parser.add_argument("--title-suffix",
                        type=str,
                        nargs='?',
                        default='',
                        help="Adds the words to the end of the histogram title")
    parser.add_argument("--use-ll",
                        action='store_true',
                        help="Uses the log-likelihood fitting procedure")
    parser.add_argument("--do-ktbin",
                        action='store_true',
                        help="Processes all kt-binned correlation functions (if any)")
    parser.add_argument("datafile", help="ROOT filename to analyze")
    parser.add_argument("output_filename",
                        nargs='?',
                        default=None,
                        help="Output root filename to store results, defaults to 'qinv' "
                             "inserted into the input name. A value of '-' indicates no "
                             "output file")
    return parser


def loglikely_fit(num, den, ModelClass=GaussianModelFSI, fit_range=(0, 0.16)):
    """
    Do a fit via the loglikelyhood method.

    Parameters:
        num, den (Histogram): Correlation numerator/denominator pair
        ModelClass (type): Subclass of lmfit.Model, implementing the
            classmethod `as_loglike` which accepts lmfit parameters
            and the numerator/deonimator pair; this method is used in
            the lmfit.minimize function.
        fit_range (Tuple): Tuple containing beginning and ending qinv
            points, defining the domain of the fit.
    """
    qinv_params = ModelClass.guess()
    ratio = num / den
    fit_slice = ratio.x_axis.get_slice(fit_range)
    x = ratio.x_axis.bin_centers[fit_slice]

    qinv_fit = minimize(ModelClass.as_loglike,
                        qinv_params,
                        args=(x, num[fit_slice], den[fit_slice]))
    return qinv_fit


def get_fitting_procedure():
    """
    ** currently unused **

    Function (which will be) used to select a fitting method based on
    program arguments.
    """
    return loglikely_fit


def do_timed_fit(fitter):
    """
    Runs a fitting methods and prints the report and time it took to run

    Args:
        fitter (callable): Callable taking no arguments and returning a
            fit object - this probably should be a lambda
    """
    TIMESTART = time.monotonic()
    fit_info = fitter()
    TIME_DELTA = time.monotonic() - TIMESTART
    time_per_call = TIME_DELTA * 1e3 / fit_info.nfev
    report_fit(fit_info)
    print("fitting time %0.3fs (%0.3f ms/call)\n\n" % (TIME_DELTA, time_per_call))
    return fit_info


def fit_to_TF1(fit_res, x):
    """
    Takes a fit result and returns a 1D ROOT function (TF1)
    """
    print(dir(fit_res), )# .model)

def get_data():
    pass

def main(argv):
    """ Main Function of qinv_fit """
    # parse user arguments
    args = argument_parser().parse_args(argv)

    norm_x_range = tuple(map(float, args.norm_range.split(':')))
    output_domain = tuple(map(float, args.output_domain.split(':')))

    # create the femtolist from the input file
    femtolist = Femtolist(args.datafile)

    # create outputfile
    if args.output_filename is None:
        ext_position = args.datafile.rfind('.')
        args.output_filename = args.datafile[:ext_position] + ".qinv" + args.datafile[ext_position:]

    output_file = (ROOT.TFile(args.output_filename, 'RECREATE')
                   if args.output_filename != '-'
                   else MagicMock())

    # loop through each analysis in femtolist
    for analysis in femtolist:
        print("***", analysis.name)

        # model = GaussianModelFSI()
        # params = model.guess()
        # model.fit(params, args=analysis.qinv_pair)
        fit_res = do_timed_fit(lambda: loglikely_fit(*analysis.qinv_pair))
        # fit_to_TF1(fit_res, None)
        # ROOT.TF1(np.array([1,1,1,1.0,], dtype=np.float64))
        print(analysis.name, fit_res.params['radius'].value, fit_res.params['radius'].stderr)

        if args.do_ktbin:
            print("\n  :: Kt binned fits ::\n")
            def split_value_error(v):
                return np.array([v.value, v.stderr])

            kt_info = []
            radius_data = []
            lam_data = []
            for ktbin, subanalysis in enumerate(analysis.kt_binned_pairs):
                # q = np.average()
                q = np.mean(tuple(
                    map(float, subanalysis.GetName().split('_'))
                ))
                # q =subanalysis.GetName().split('_')
                pair = analysis.qinv_pair_in_kt_bin(ktbin)
                # fit_res = do_timed_fit(lambda: loglikely_fit(*pair))
                fit_res = loglikely_fit(*pair)
                kt_info.append(q)
                radius_data.append(split_value_error(fit_res.params['radius']))
                lam_data.append(split_value_error(fit_res.params['lam']))
                # kt_info.append((q, , split_value_error(fit_res.params['lam'])))

            mt_info = np.sqrt(np.array(kt_info) ** 2 + 0.138 ** 2)
            radius_data, lam_data = np.array(radius_data).T, np.array(lam_data).T

            # radius_data = np.vstack((kt_info, radius_data[0], radius_data[1]))
            # print(kt_info.T[0])
            # rh.SetTitle("#pi Radius Fit Results (k_{T} Binned); <k_{T}> (GeV); R_{inv} (fm)")
            # lh = ROOT.TGraphErrors(len(kt_info))
            # lh.SetTitle("#pi Lambda Fit Results (k_{T} Binned); <k_{T}> (GeV); Lambda (fm)")
            # for i, (x, r, l) in enumerate(kt_info):
            #     rh.SetPoint(i, x, r[0])
            #     lh.SetPoint(i, x, l[0])
            #     rh.SetPointError(i, 0, r[1])
            #     lh.SetPointError(i, 0, l[1])


            numpoints = 7
            assert len(kt_info) == numpoints
            c0 = ROOT.TCanvas("radius")

            xerr = np.zeros(numpoints)
            xval = np.array([0.287195, 0.375873, 0.469237, 0.565494, 0.66286, 0.759927, 0.877914])
            yval = np.array([8.98, 8.385, 7.775, 7.275, 6.675, 6.295, 5.825])
            yerr = np.array([0.06, 0.09, 0.08, 0.105, 0.095, 0.115, 0.11])
            p9053_d32x1y1 = ROOT.TGraphErrors(numpoints, xval, yval, xerr, yerr)
            p9053_d32x1y1.SetName("/HepData/9053/d32x1y1")
            p9053_d32x1y1.SetTitle("/HepData/9053/d32x1y1; <M_{T}> GeV; R_{inv}")
            p9053_d32x1y1.Write()
            p9053_d32x1y1.Draw("AP")
            # print(mt_info, radius_data[0])
            rh = ROOT.TGraphErrors(len(mt_info), mt_info, np.copy(radius_data[0]), xerr, np.copy(radius_data[1]))
            for i, (x, y) in enumerate(zip(mt_info, radius_data)):
                pass
            print(mt_info)
            print(radius_data[0])
            print(radius_data[1])
            rh.SetName("radius")
            rh.Draw("sameAP")
            # wait()

            c1 = ROOT.TCanvas("lambda")
            lh = ROOT.TGraphErrors(len(mt_info), mt_info, np.copy(lam_data[0]), xerr, np.copy(lam_data[1]))
            lh.SetName("lambda")
            lh.SetTitle("#lambda Parameter; <m_{T}> (GeV); #lambda")
            lh.Draw("AP")


            ROOT.gApplication._threaded = True
            ROOT.gApplication.Run(True)


            rh.Write()
            # print(kt_info)
            # rh.Draw()
            #
            # lh.Draw()
            output_file.Write()

            break
        break
            # input()

        continue

        print("\n:::Chi-Squared Fit:::::\n")
        # norm_ratio = num / np.sum(num[0.7:0.8]) / (den / np.sum(den[0.7:0.8]))
        norm_ratio = num / den


        # ModelClass
        fit_method = 'leastsq'

        b = norm_ratio.bin_at(0.2)
        fit_args = num.x_axis.bin_centers[:b], (norm_ratio.data[:b], norm_ratio.errors[:b])

        tfit = minimize(fitfunc_qinv, qinv_params, args=fit_args, method=fit_method)

        fitx = np.linspace(0, 0.1, 100)
        fity = fitfunc_qinv(tfit.params, fitx)
        report_fit(tfit)
        print("\n:::LL-Fit:::::\n")

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

        plt.show()

    output_file.Close()

if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))

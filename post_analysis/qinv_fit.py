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
from os.path import basename
from collections import OrderedDict
from unittest.mock import MagicMock
from argparse import ArgumentParser, Action
from lmfit import minimize, Parameters, report_fit
from rootpy.plotting import HistStack
from rootpy.plotting.utils import draw

from stumpy import Histogram
from pionpion import Femtolist
from pionpion.fit import fitfunc_qinv, fitfunc_qinv_gauss_ll
from post_analysis.fitting.gaussian import (
    GaussianModel,
    GaussianModelCoulomb,
    GaussianModelFSI,
)
from momentum_correction_by_division import Corrections

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
    parser.add_argument("--correction-file",
                        nargs='?',
                        default=None,
                        help="File containing momentum correction histograms.")
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
    parser.add_argument("datafile", help="ROOT filename to analyze. "
                                         "Separate filenames by commas if you want more than"
                                         "one file in femtolist")
    parser.add_argument("output_filename",
                        nargs='?',
                        default=None,
                        help="Output root filename to store results, defaults to 'qinv' "
                             "inserted into the input name. A value of '-' indicates no "
                             "output file")
    return parser


def simple_fit(ratio, ModelClass=GaussianModelFSI, fit_range=(1, 0.16)):
    qinv_params = ModelClass.guess()
    fit_slice = ratio.x_axis.get_slice(fit_range)
    x = ratio.x_axis.bin_centers[fit_slice]
    return minimize(ModelClass.as_resid,
                    qinv_params,
                    args=(x, ratio[fit_slice], ratio.errors[fit_slice]))


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


def get_fitting_procedure(args):
    """
    Function (which will be) used to select a fitting method based on
    program arguments.
    """
    return loglikely_fit if args.use_ll else simple_fit


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


class QinvFit:
    """
    """

    def __init__(self, analysis, args):
        """
        Construct a fit from an analysis (located in a femtolist)
        """
        print("***", analysis.name)
        self.name = analysis.name
        self.analysis = analysis
        self.fit_procedure = get_fitting_procedure(args)

        # self.fit_res = self.do_fit(analysis.qinv_pair)

        if not args.do_ktbin:
            self.kt_binned_fits = None
        else:
            print("\n  :: Kt binned fits ::\n")
            self.kt_binned_fits = OrderedDict()

            for ktbin, subanalysis in enumerate(analysis.kt_binned_pairs):
                name = subanalysis.GetName()
                q = np.mean(tuple(map(float, name.split('_'))))
                # q =subanalysis.GetName().split('_')
                pair = analysis.qinv_pair_in_kt_bin(ktbin)
                fit_res = self.do_fit(pair)
                rad = fit_res.params['radius']
                lam = fit_res.params['lam']

                self.kt_binned_fits[name] = {
                    'kt': q,
                    'radius': rad.value,
                    'radius_err': rad.stderr,
                    'lambda': lam.value,
                    'lambda_err': lam.stderr,
                }

    @property
    def corrections(self):
        "Return momentum correction histogram for the qinv fit (if available)"
        global corrections
        try:
            return corrections[self.name]
        except:
            return None

    def do_fit(self, qinv_pair):
        return self.fit_procedure(*qinv_pair)

    @staticmethod
    def fit_result_to_plot(fit_res):
        rplot = ROOT.TGraphErrors(npoints, x, r, np.zeros(npoints), re)
        rplot.SetName("CF")
        output.Add(rplot)

    def write(self, file):
        """
        Write the objects to the file. If file is TDirectory
        (including TFiles) this is 'cd' to and written
        """

        if isinstance(file, ROOT.TDirectory):
            print("into", file)
            file.cd()
            output = ROOT.TObjArray()
            output.SetName(self.name)
            num, den = self.analysis.qinv_pair
            ratio = num / den
            print('...', num.data[-1], den.data[-1])
            norm = self.fit_res.params['norm'].value
            print('norm:', norm)
            print(ratio.data[-1])
            ratio /= norm
            print(ratio.data[-1])
            output.Add(ratio.AsRootHist())
            # output.Add(self.fit_result_to_plot(self.fit_res))

            if self.kt_binned_fits:
                f = self.kt_binned_fits.values()

                x = np.array([b['kt'] for b in f])
                r = np.array([b['radius'] for b in f])
                re = np.array([b['radius_err'] for b in f])
                l = np.array([b['lambda'] for b in f])
                le = np.array([b['lambda_err'] for b in f])
                npoints = len(x)

                rplot = ROOT.TGraphErrors(npoints, x, r, np.zeros(npoints), re)
                rplot.SetName("radius")
                output.Add(rplot)
                lplot = ROOT.TGraphErrors(npoints, x, l, np.zeros(npoints), le)
                lplot.SetName("lambda")
                output.Add(lplot)

            output.Write()


def main(argv):
    """ Main Function of qinv_fit """
    global corrections

    # parse user arguments
    args = argument_parser().parse_args(argv)

    # assign global corrections built from the correction file
    if args.correction_file:
        corrections = Corrections(args.correction_file)
    else:
        corrections = None

    # get normalization and output domains from arguments
    norm_x_range = tuple(map(float, args.norm_range.split(':')))
    output_domain = tuple(map(float, args.output_domain.split(':')))

    # get filenames separated by commas
    femtolist_names = tuple(map(str.strip, args.datafile.split(',')))

    # create the femtolist(s) from the input file(s)
    femtolists = tuple(map(Femtolist, femtolist_names))

    # generate filename from (first) input name
    if args.output_filename is None:
        fname, _, ext = femtolist_names[0].rpartition('.')
        args.output_filename =  "%s.qinv.%s" % (fname, ext)

    # create outputfile (Mock object if output_filename is '-')
    if args.output_filename == '-':
        output_file = MagicMock()
    else:
        output_file = ROOT.TFile(args.output_filename, 'RECREATE')

    # loop through each file
    for femtolist in femtolists:
        # if multiple inputs, store in multiple 'subdirs'
        if len(femtolists) == 1:
            d = output_file
        else:
            d = output_file.mkdir(femtolist.filename.rstrip(".root"))

        # Create fit object from each analysis in femtolist
        for analysis in femtolist:

            d.mkdir(analysis.name).cd()

            num, den = analysis.qinv_pair
            ratio = num / den
            ratio.title = "Corrected Correlation Function"
            print(ratio.errors[:5])
            if corrections:
                norm_correction = corrections[analysis.name]
                assert ratio.shape == norm_correction.shape, \
                       "{} ≠ {}".format(ratio.shape, norm_correction.shape)
                ratio *= norm_correction
            print(ratio.errors[:5])

            fit_res = simple_fit(ratio)
            report_fit(fit_res)

            # import matplotlib.pyplot as plt
            # plt.errorbar(x=list(range(30)), y=ratio.data[:30], yerr=ratio.errors[:30])
            # plt.plot(GaussianModelFSI.gauss(
            #     ratio.x_axis.bin_centers[:30],
            #     **fit_res.params))
            # plt.show()


            num, den = analysis[analysis.QINV_NUM_PATH], analysis[analysis.QINV_DEN_PATH]

            # create ratio
            root_ratio = num.Clone()
            root_ratio.SetTitle("Corrected Correlation Function")
            root_ratio.Divide(den)

            # apply correction
            if corrections:
                norm_correction = corrections[analysis.name]
                assert num.GetNbinsX() == den.GetNbinsX() == norm_correction.shape[0]
                for i, c in enumerate(norm_correction, 1):
                    x = root_ratio.GetBinContent(i)
                    e = root_ratio.GetBinError(i)
                    root_ratio.SetBinContent(i, x * c)
                    root_ratio.SetBinError(i, e * c)
                root_ratio.Write("CorrelationFunction")

            #
            fit_res = simple_fit(Histogram.BuildFromRootHist(root_ratio))
            report_fit(fit_res)

            x = np.linspace(0, 1.0, 300)
            y = GaussianModelFSI.gauss(x, **fit_res.params)
            plot = ROOT.TGraph(len(x), x, y)
            plot.Write("FitPlot")
            # x = np.copy(ratio.x_axis.bin_centers[:30])
            # y = np.copy(GaussianModelFSI.gauss(x, **fit_res.params))
            # ye = np.copy(np.sqrt(np.mean(data[2] ** 2, axis=1)))
            #
            # fit_plot = ROOT.TGraphErrors(len(x), x, y, np.zeros(len(x)), ye)
            # plt.plot(
            #     ratio.x_axis.bin_centers[:30],
            #     **fit_res.params))
            # qfit = QinvFit(analysis, args)
            # report_fit(qfit.fit_res)

            # o = d.mkdir(analysis.name)
            # print('.>.', o)
            # if o != None:
            #     qfit.write(o)
            #     print('wrote', qfit)

    output_file.Write()
    output_file.Close()

if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))

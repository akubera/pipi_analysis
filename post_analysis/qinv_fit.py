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


class QinvFit:
    """
    """

    def __init__(self, analysis, args):
        """
        Construct a fit from an analysis (located in a femtolist)
        """
        print("***", analysis.name)
        self.fit_res = fit_res = self.do_fit(analysis.qinv_pair)
        self.name = analysis.name

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

    def do_fit(self, qinv_pair):
        return loglikely_fit(*qinv_pair)

    def write(self, file):
        """
        Write the objects to the file. If file is TDirectory
        (including TFiles) this is 'cd' to and written
        """

        if isinstance(file, ROOT.TDirectory):
            file.cd()
            output = ROOT.TObjArray()
            output.SetName(self.name)
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
    # parse user arguments
    args = argument_parser().parse_args(argv)

    norm_x_range = tuple(map(float, args.norm_range.split(':')))
    output_domain = tuple(map(float, args.output_domain.split(':')))

    femtolist_names = tuple(map(str.strip, args.datafile.split(',')))

    # create the femtolist(s) from the input file(s)
    femtolists = tuple(map(Femtolist, femtolist_names))

    # generate filename from input name
    if args.output_filename is None:
        filename = femtolist_names[0]
        ext_position = filename.rfind('.')
        fname, ext = filename[:ext_position], filename[ext_position:]
        args.output_filename =  "%s.qinv%s" % (fname, ext)

    # create outputfile (Mock object if output_filename is '-')
    output_file = (ROOT.TFile(args.output_filename, 'RECREATE')
                   if args.output_filename != '-'
                   else MagicMock())

    # Create fit object from each analysis in femtolist
    for femtolist in femtolists:
        fname = basename(femtolist._file.GetName().rstrip(".root"))
        d = output_file.mkdir(fname)
        d.cd()
        for analysis in femtolist:
            qfit = QinvFit(analysis, args)
            o = d.mkdir(analysis.name)
            if o != None:
                qfit.write(o)

    output_file.Write()
    output_file.Close()

if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))

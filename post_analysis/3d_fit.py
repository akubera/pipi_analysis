#!/usr/bin/env python3
#
# post_analysis/3d_fit.py
#

import sys
import numpy as np
from argparse import ArgumentParser
from collections import defaultdict
import types
import numbers
import ctypes
import time
from pionpion.analysis import Analysis


TSTART = time.monotonic()
print("loading ROOT... ", end='', flush=True, file=sys.stderr)
from lmfit import minimize, Parameters, report_fit
import ROOT
from ROOT import (
    TFile,
    TMinuit,
    TApplication,
    TObjString,
    TGraph,
)
import root_numpy
from pionpion.histogram import Histogram

print("Done (%fs)" % (time.monotonic() - TSTART), file=sys.stderr)

CACHE = []
STORED_CANVASES = []


def gen_canvas():
    """
    Create a new canvas, cached so it wont go out of scope.
    """
    global STORED_CANVASES
    name = "c%0.2x" % len(STORED_CANVASES)
    # print("Creating Canvas %s" % name)
    canvas = ROOT.TCanvas(name, "Canvas", 200, 10, 700, 500)
    STORED_CANVASES.append(canvas)
    return canvas

# gen_canvas = iter(gen_canvas())


def get_root_object(obj, paths):
    if isinstance(paths, (list, tuple)):
        path = paths.pop(0)
    else:
        path, paths = paths, []

    key, *rest = path.split('.', 1)
    try:
        new_obj = obj.Get(key)
    except AttributeError:
        new_obj = obj.FindObject(key)

    if new_obj == None and len(paths) is not 0:
        return get_root_object(obj, paths)
    elif new_obj == None or len(rest) is 0:
        return new_obj
    else:
        return get_root_object(new_obj, rest[0])


def hist_method_to_array(hist, func):
    nbins = hist.GetNbinsX()
    func = getattr(hist, func)
    return np.array(list(map(func, range(1, nbins))))


def get_ratio(name, num, den, norm_x_ranges, *, cache=True):
    """
    Returns the normalized ratio of the two histograms
    """
    if isinstance(norm_x_ranges[0], numbers.Number):
        norm_x_ranges = [norm_x_ranges]

    num_scale, den_scale = 0.0, 0.0

    for norm_x_range in norm_x_ranges:
        num_scale += num.Integral(*map(num.FindBin, norm_x_range))
        den_scale += den.Integral(*map(den.FindBin, norm_x_range))

    ratio = num.Clone(name)
    ratio.Divide(num, den, 1.0 / num_scale, 1.0 / den_scale)
    ratio.SetStats(False)

    if cache:
        CACHE.append(ratio)

    return ratio


parser = ArgumentParser()
parser.add_argument("filename", help="root filename to analyze")
parser.add_argument("output",
                    nargs='?',
                    default='Result.root',
                    help="root filename to analyze")
args = parser.parse_args()

file = TFile(args.filename, 'READ')

femtolist = get_root_object(file, ['femtolist', 'PWG2FEMTO.femtolist'])

if femtolist == None:
    print("Could not find femtolist", file=sys.stderr)
    sys.exit(1)

output = TFile(args.output, 'RECREATE')

# analysis = get_root_object(femtolist, "PiPiAnalysis_00_10_pip")


for analysis in femtolist:

    analysis_name = analysis.GetName()

    output.mkdir(analysis_name)
    output.cd(analysis_name)

    print("********* %s **********" % analysis_name)

    analysis_meta = Analysis.load_metadata(analysis.Last())
    if analysis_meta is None:
        print("Analysis '%s' is missing metadata. Skipping")
        continue

    track_meta = analysis_meta['AliFemtoSimpleAnalysis']['AliFemtoESDTrackCut']
    print(" Charge:", track_meta['charge'])
    print(" Mass:", track_meta['mass'])
    print(" Pt:", track_meta['pt']['minimum'], '->', track_meta['pt']['maximum'])

    num = get_root_object(analysis, ["Numc_qinv_pip", "Numc_qinv_pim"])
    den = get_root_object(analysis, ["Denc_qinv_pip", "Denc_qinv_pim"])

    if num == None or den == None:
        print("Bad analysis", analysis_name)
        print('  num:', num)
        print('  den:', den)
        continue

    charge = int(track_meta['charge'])
    chstr = '-' if charge < 0 else '+' if charge > 0 else '0'

    cf_title = "#pi^{{ %s }} {title} CF; {units} (GeV); C({units})" % (chstr)
    make_cf_title = cf_title.format

    norm_x_range = 0.4, 0.7
    num_norm_bin_range = map(num.FindBin, norm_x_range)
    den_norm_bin_range = map(num.FindBin, norm_x_range)

    num_scale = 1.0 / num.Integral(*num_norm_bin_range)
    den_scale = 1.0 / den.Integral(*den_norm_bin_range)

    ratio = get_ratio('ratio', num, den, (0.4, 0.7))
    ratio.SetTitle(make_cf_title(title='Q_{inv}', units='q_{inv}'))
    ratio.Write()

    q3d_num = get_root_object(analysis, ["Num_q3D_pip", "Num_q3D_pim"])
    q3d_den = get_root_object(analysis, ["Den_q3D_pip", "Den_q3D_pim"])

    if q3d_num == None or q3d_den == None:
        print("No 3D histogram found in", analysis_name)
        continue

    from pionpion.q3d import Q3D

    num_hist_3d = Q3D(q3d_num)
    den_hist_3d = Q3D(q3d_den)


    print('   ', num_hist_3d[-.1:.1, -.1:.1, 0.0])
    # l = num_hist_3d.bin_at(slice(None), 0.1, 0.2)
    # print('   ', num_hist_3d.value_at(0.1, 0.1, 0.2))
    # print('   ', num_hist_3d.value_in(*l))
    # # print("   ", we[0.0, -0.1:0.5, 0.0])
    # bins = tuple(axis.FindBin(0.0) for axis in we._axes)
    # print("   ", bins)
    # print("   ", we._ptr.GetBinContent(*bins))
    # print("   ", we.error[10, 10, 10])
    # print("  >", we._ptr.GetBinError(10, 10, 10))

    y_dom = (-0.01, 0.01)
    z_dom = (-0.00, 0.00)
    q_out_num = num_hist_3d.projection_out(y_domain=y_dom, z_domain=z_dom)
    q_out_num_new = num_hist_3d.project_1d(0, y_dom, z_dom)
    print(np.shape(q_out_num))
    print(np.shape(q_out_num_new))
    # print(q_out_num)
    # print(q_out_num_new)
    print(all(q_out_num_new == q_out_num))
    out_pro_bin_list = [
        q3d_num.GetYaxis().FindBin(y_dom[0]),
        q3d_num.GetYaxis().FindBin(y_dom[1]),
        q3d_num.GetZaxis().FindBin(z_dom[0]),
        q3d_num.GetZaxis().FindBin(z_dom[1]),
    ]
    print("projection X bins:", out_pro_bin_list)
    num_qout = q3d_num.ProjectionX("num_qout", *out_pro_bin_list)
    num_qout_a = root_numpy.hist2array(num_qout, include_overflow=True)
    print("==>")
    print("", q_out_num[:8])
    print("", q_out_num_new[:8])
    print("", num_qout_a[:8])
    diff = num_qout_a - q_out_num_new

    print("", diff[:10])
    print("", num_qout_a == q_out_num_new)
    break


    den_qout = q3d_den.ProjectionX("den_qout")

    ratio_qo = get_ratio('ratio_qo', num_qout, den_qout, [(-0.4, -0.7), (0.4, 0.7)])
    ratio_qo.SetTitle(make_cf_title(title='Q_{out}', units='q_{out}'))
    ratio_qo.Write()

    X_Zero = ratio_qo.GetXaxis().FindBin(0)
    Y_Zero = ratio_qo.GetYaxis().FindBin(0)
    Z_Zero = ratio_qo.GetZaxis().FindBin(0)

    bin_offset = 4

    bins = {
        'xmin': X_Zero - bin_offset,
        'xmax': X_Zero + bin_offset,
        'ymin': Y_Zero - bin_offset,
        'ymax': Y_Zero + bin_offset,
        'zmin': Z_Zero - bin_offset,
        'zmax': Z_Zero + bin_offset,
    }



    num_qside = q3d_num.ProjectionY("num_qside")
    den_qside = q3d_den.ProjectionY("den_qside")

    ratio_qs = get_ratio('ratio_qs', num_qside, den_qside, [(-0.4, -0.7), (0.4, 0.7)])
    ratio_qs.SetTitle(make_cf_title(title='Q_{side}', units='q_{side}'))
    ratio_qs.Write()

    num_qlong = q3d_num.ProjectionZ("num_qlong")
    den_qlong = q3d_den.ProjectionZ("den_qlong")

    ratio_ql = get_ratio('ratio_ql', num_qlong, den_qlong, [(-0.4, -0.7), (0.4, 0.7)])
    ratio_ql.SetTitle(make_cf_title(title='Q_{long}', units='q_{long}'))
    ratio_ql.Write()


    #
    # Do Fit
    #

    X = hist_method_to_array(ratio, 'GetBinCenter')
    Y = hist_method_to_array(ratio, 'GetBinContent')
    E = hist_method_to_array(ratio, 'GetBinError')

    stop_fit = ratio.FindBin(0.25)

    qinv_params = Parameters()
    qinv_params.add('radius', value=0.5, min=0.0)
    qinv_params.add('lam', value=0.5)  # , min=0.0, max=1.0)

    def fit_qinv(params, x, data=None):
        model = 1 + params['lam'] * np.exp(list(-(x * params['radius']) ** 2))
        if data is None:
            return model

        shape = np.shape(data)
        func_count = shape[0] / 2

        if func_count % 1:
            raise ValueError("Data shape not multiple of 2. Mismatched data and errors")

        # resid = sum(np.sqrt((data[i] - model) ** 2 / data[i + 1] ** 2)
        #             for i in range(0, shape[0], 2))

        resid = model - data[0]
        res = np.sqrt( resid ** 2 / data[1] ** 2 )
        return res

    x_vals = X[:stop_fit]
    y_vals = Y[:stop_fit]
    e_vals = E[:stop_fit]

    qinv_fit = minimize(fit_qinv, qinv_params, args=(x_vals, (y_vals, e_vals)))
    report_fit(qinv_fit)
    FIT_X = np.linspace(300, (X[0], X[-1]))
    FIT_Y = fit_qinv(qinv_fit.params, FIT_X)

    canvas_qinv = gen_canvas()
    # canvas_qinv.cd(1)

    fit_plot = TGraph(len(FIT_X), FIT_X, FIT_Y)
    CACHE.append(fit_plot)

    ratio.Draw()
    fit_plot.SetLineColor(2)
    fit_plot.Draw("same")
    canvas_qinv.Draw()



    #
    # Qinv - Kt binned
    #
    kt_qinv = get_root_object(analysis, ["KT_Qinv"])
    if kt_qinv != None:
        for ktbin in kt_qinv:
            ktn = get_root_object(ktbin, ["Numc_qinv_pip", "Numc_qinv_pim"])
            ktd = get_root_object(ktbin, ["Denc_qinv_pip", "Denc_qinv_pim"])



    continue

    #
    #
    #

    def split_hist(hist):
        return (
            hist_method_to_array(hist, 'GetBinCenter'),
            hist_method_to_array(hist, 'GetBinContent'),
            hist_method_to_array(hist, 'GetBinError'),
        )

    Xo, Yo, Eo = split_hist(ratio_qo)
    Xs, Ys, Es = split_hist(ratio_qs)
    Xl, Yl, El = split_hist(ratio_ql)

    qinv_params = Parameters()
    qinv_params.add('r_out', value=0.5, min=0.0)
    qinv_params.add('r_side', value=0.5, min=0.0)
    qinv_params.add('r_long', value=0.5, min=0.0)
    qinv_params.add('lam', value=0.5, min=-10.0, max=10.0)

    def fit_3d_q(params, osl, data=None):
        """
        Do 3D Gaussian fit of data.

        y = 1 + λ exp( -((qo * [Ro])^2 + (qs * [Rs])^2 + (ql * [Rl])^2) )

        """
        # split x into components
        o, s, l = osl
        t = sum((o * params['r_out']) ** 2, (s * params['r_side']) ** 2, (l * params['r_long']) ** 2)
        model = 1 + params['lam'] * np.exp(list(-t))
        if data is None:
            return model



input()

    # ratio.Draw()
    # break

output.Close()

# app = TApplication.GetApplications()[0]
# print(app)
# app.Run()

# input()

# print(file)
# params = FitParams()
# fitter = TMinuit()

# for i, param in enumerate(fit_params):
#     fitter.DefineParameter(i, param.name, param.ival)
#     # fitter.DefineParameter(iPar, fMinuitParNames[iPar], fMinuitParInitial[iPar], startingStepSize, fMinuitParMinimum[iPar], fMinuitParMaximum[iPar]);
# print(fitter)

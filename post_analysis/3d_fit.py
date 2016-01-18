#!/usr/bin/env python3
#
# post_analysis/3d_fit.py
#

import sys
import numpy as np
from argparse import ArgumentParser
from collections import defaultdict
import itertools
import types
import numbers
import ctypes
import time
from pionpion.root_helpers import get_root_object
from pionpion.analysis import Analysis
from pionpion.q3d import Q3D
from pionpion.fit import (
    fitfunc_qinv,
    fitfunc_3d,
)
from pprint import pprint

import matplotlib as ml
import matplotlib.pyplot as plt

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

NUM_QINV_PATH = "Num_qinv_pip Num_qinv_pim Numc_qinv_pip Numc_qinv_pim".split()
DEN_QINV_PATH = "Den_qinv_pip Den_qinv_pim Denc_qinv_pip Denc_qinv_pim".split()
NUM_Q3D_PATH = ["Num_q3D_pip", "Num_q3D_pim"]
DEN_Q3D_PATH = ["Den_q3D_pip", "Den_q3D_pim"]


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
TRACK_CUT_INFO_STR = """\
 Charge: {charge}
 Mass: {mass}
 Pt: {pt[minimum]} -> {pt[maximum]}
"""


def do_qinv_analysis(num, den, cf_title="CF; q (GeV); CF(q)", output_imagename='qinv.png'):
    """
    Code performing the qinv analysis - should probably be moved to a submodule
    """

    norm_x_range = 0.8, 1.1
    num_norm_bin_range = map(num.FindBin, norm_x_range)
    den_norm_bin_range = map(num.FindBin, norm_x_range)

    num_scale = 1.0 / num.Integral(*num_norm_bin_range)
    den_scale = 1.0 / den.Integral(*den_norm_bin_range)

    ratio = get_ratio('ratio', num, den, norm_x_range)
    ratio.SetTitle(cf_title)
    ratio.Write()

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

    x_vals = X[:stop_fit]
    y_vals = Y[:stop_fit]
    e_vals = E[:stop_fit]

    data = (y_vals, e_vals)

    TIMESTART = time.monotonic()
    qinv_fit = minimize(fitfunc_qinv, qinv_params, args=(x_vals, data))
    TIME_DELTA = time.monotonic() - TIMESTART
    report_fit(qinv_fit)
    print("fitting time %0.3fs (%0.3f ms/call)" % (TIME_DELTA, TIME_DELTA * 1e3 / qinv_fit.nfev))

    FIT_X = np.linspace(X[0], X[-1], 300)
    FIT_Y = fitfunc_qinv(qinv_fit.params, FIT_X)

    canvas_qinv = gen_canvas()
    # canvas_qinv.cd(1)
    ratio.GetXaxis().SetRangeUser(0.0, 0.5)
    ratio.Draw()

    fit_plot = TGraph(len(FIT_X), FIT_X, FIT_Y)
    CACHE.append(fit_plot)

    fit_plot.SetLineColor(2)
    fit_plot.Draw("same")
    canvas_qinv.Draw()
    canvas_qinv.SaveAs(output_imagename)
    # output_image = ROOT.TImage.Create()
    # output_image.FromPad(canvas_qinv)
    # output_image.WriteImage(output_imagename)


# Loop over analyses
for analysis in femtolist:

    analysis_name = analysis.GetName()

    output.mkdir(analysis_name)
    output.cd(analysis_name)

    print("********* %s **********" % analysis_name)

    analysis_meta = Analysis.load_metadata(analysis.Last())
    if analysis_meta is None:
        print("Analysis '%s' is missing metadata. Skipping")
        continue
    from pprint import pprint
    pprint(analysis_meta)
    track_meta = analysis_meta['AliFemtoSimpleAnalysis']['AliFemtoESDTrackCut']
    print(TRACK_CUT_INFO_STR.format(**track_meta))

    charge = int(track_meta['charge'])
    chstr = '-' if charge < 0 else '+' if charge > 0 else '0'
    cf_title = "#pi^{{ %s }} {title} CF; {units} (GeV); C({units})" % (chstr)
    make_cf_title = cf_title.format

    #
    # Qinv
    #

    num = get_root_object(analysis, NUM_QINV_PATH)
    den = get_root_object(analysis, DEN_QINV_PATH)

    if num == None or den == None:
        print("Missing Qinv plots")
        print('  num:', num)
        print('  den:', den)
    else:
        print(" ***** Q_inv Study *****\n")
        qinv_title = make_cf_title(title='Q_{inv}', units='q_{inv}')
        do_qinv_analysis(num, den, cf_title=qinv_title, output_imagename=analysis_name + '_qinv.png')

    #
    # Fake Qinv - Kt binned
    #
    fake_qinv_num = get_root_object(analysis, ["fakeNum_q3D_pip"])
    fake_qinv_den = get_root_object(analysis, ["FakeDen_q3D_pip"])
    if fake_qinv_num == None or fake_qinv_den == None:
        print("Missing fake_qinv", fake_qinv_num, fake_qinv_den)
    else:
        print("\n\n")
        print(" ***** Fake Q_inv Study *****\n")
        do_qinv_analysis(fake_qinv_num, fake_qinv_den, cf_title="Fake Q_inv", output_imagename=analysis_name + '_fake_qinv.png')

    #
    # Qinv - Kt binned
    #
    kt_qinv = get_root_object(analysis, ["KT_Qinv"])
    if kt_qinv != None:
        for ktbin in kt_qinv:
            ktn = get_root_object(ktbin, NUM_QINV_PATH)
            ktd = get_root_object(ktbin, DEN_QINV_PATH)


    #
    # 3D
    #

    q3d_num = get_root_object(analysis, NUM_Q3D_PATH)
    q3d_den = get_root_object(analysis, DEN_Q3D_PATH)

    if q3d_num == None or q3d_den == None:
        print("No 3D histogram found in", analysis_name)
        continue

    print(" ***** 3D Study Q{osl} *****\n")

    q3d_params = Parameters()
    q3d_params.add('r_out', value=6.0, min=0.0)
    q3d_params.add('r_side', value=6.0, min=0.0)
    q3d_params.add('r_long', value=6.0, min=0.0)
    q3d_params.add('lam', value=1.0)
    q3d_params.add('norm', value=1.0, min=0.0)

    hist_3d = Q3D(q3d_num, q3d_den)
    hist_3d.ratio._ptr.Write()
    out_side = hist_3d.ratio.project_2d(0, 1, (-0.03, 0.03), bounds_x=(0.0, None))

    fig = plt.figure(figsize=(6, 3.2))

    ax = fig.add_subplot(111)
    ax.set_title('colorMap')
    plt.contourf(out_side)
    ax.set_aspect('equal')

    cax = fig.add_axes([0.12, 0.1, 0.78, 0.8])
    cax.get_xaxis().set_visible(True)
    cax.get_yaxis().set_visible(False)
    cax.patch.set_alpha(0)
    cax.set_frame_on(False)
    plt.colorbar(orientation='vertical')
    # plt.show()


    # domains_ranges = (-0.2, 0.2), (-0.2, 0.2), (-0.2, 0.2)
    domains_ranges = (2, -2), (2, -2), (2, -2)
    # domains_ranges = (1, -2), (1, -2), (1, -1)
    slices = hist_3d.num.getslice(*domains_ranges)
    # slices = slice(None), slice(None), slice(None)

    t = time.monotonic()
    dom = hist_3d.num.bounded_domain(*slices)

    # mask so that only bins with non-zero errors are chosen
    ratio_err = hist_3d.ratio.error[slices].flatten()
    error_mask = ratio_err != 0
    dom = dom[error_mask]
    ratio_err = ratio_err[error_mask]
    ratio = hist_3d.ratio_data[slices].flatten()[error_mask]

    TIMESTART = time.monotonic()
    fit_res = minimize(fitfunc_3d, q3d_params, args=(dom, (ratio, ratio_err)))
    TIME_DELTA = time.monotonic() - TIMESTART
    report_fit(fit_res)
    print("fitting time %0.3fss (%0.3f ms/call)" % (TIME_DELTA, TIME_DELTA * 1e3 / fit_res.nfev))
    # projection_bins = hist_3d.num.bin_ranges([-0.01, 0.01], [-0.01, 0.01], [-0.01, 0.01])
    # xmin, xmax, ymin, ymax, zmin, zmax = [x for x in projection_bins for x in x]
    cr = (0.0, 2)
    xmin, xmax, ymin, ymax, zmin, zmax = hist_3d.num.centered_bin_ranges(cr, cr, cr, expand=True, inclusive=True)

    # hist_3d.ratio._ptr.Scale(1.0 / fit_res.params['norm'])
    # hist_3d.ratio_data = hist_3d.ratio_data / fit_res.params['norm']

    out_side_cnvs = ROOT.TCanvas("out_side")
    zz = hist_3d.ratio._ptr.GetZaxis().FindBin(0.0)
    zdist = 6
    hist_3d.ratio._ptr.GetZaxis().SetRange(zz - zdist, zz + zdist)
    # hist_3d.ratio._ptr.GetZaxis().SetRange(zmin, zmax)
    out_side = hist_3d.ratio._ptr.Project3D("yx")
    out_side.Write()
    out_side.SetStats(False)
    out_side.Draw("colz")
    out_side_cnvs.Draw()
    out_side_cnvs.SaveAs("OUTSIDEz0.png")
    hist_3d.ratio._ptr.GetZaxis().SetRange()

    do_rebin = False

    qout = hist_3d.ratio._ptr.ProjectionX("qout", ymin, ymax-1, zmin, zmax-1)
    qout.SetStats(False)
    qout.Write()
    norm_scale_factor = 1.0 / ((ymax - ymin) * (zmax - zmin)) / fit_res.params['norm']
    qout.Scale(norm_scale_factor)
    if do_rebin:
        qout.Rebin(2)
        qout.Scale(.5)
    qout.SetTitle("Q_{out};; CF(q_{out})")
    best_fit_X = hist_3d.ratio._axes[0].data[xmin:xmax]
    best_fit_Y = hist_3d.ratio._axes[1].data[ymin:ymax]
    best_fit_Z = hist_3d.ratio._axes[2].data[zmin:zmax]

    qo_X = np.linspace(-0.6, 0.6, 200)
    qs_X = np.linspace(-0.6, 0.6, 200)
    ql_X = np.linspace(-0.8, 0.8, 200)

    best_fit_Domain = np.array([[[x, y, z]
                                  for y in best_fit_Y
                                  for z in best_fit_Z
                                  ] for x in qo_X])
    best_fit_qout = np.array([fitfunc_3d(fit_res.params, x)
                              for x in best_fit_Domain])
    qo_Y = np.sum(best_fit_qout, axis=1) * norm_scale_factor
    assert qo_Y.shape == qo_X.shape

    qo_graph = ROOT.TGraph(len(qo_X), qo_X, qo_Y)
    qo_graph.SetLineColor(2)


    norm_scale_factor = 1.0 / ((xmax - xmin) * (zmax - zmin)) / fit_res.params['norm']

    best_fit_Domain = np.array([[[x, y, z]
                                  for x in best_fit_X
                                  for z in best_fit_Z
                                  ] for y in qs_X])
    best_fit_qout = np.array([fitfunc_3d(fit_res.params, x)
                              for x in best_fit_Domain])
    qs_Y = np.sum(best_fit_qout, axis=1) * norm_scale_factor
    assert qs_X.shape == qs_Y.shape

    qside = hist_3d.ratio._ptr.ProjectionY("qside", xmin, xmax-1, zmin, zmax-1)
    qside.SetStats(False)
    qside.Scale(norm_scale_factor)
    qside.SetTitle("Q_{side};; CF(q_{side})")
    qside.Write()

    if do_rebin:
        qside.Rebin(2)
        qside.Scale(1.0/2.0)

    qs_graph = ROOT.TGraph(len(qs_Y), qs_X, qs_Y)
    qs_graph.SetLineColor(2)



    norm_scale_factor = 1.0 / ((xmax - xmin) * (ymax - ymin)) / fit_res.params['norm']

    best_fit_Domain = np.array([[[x, y, z]
                                  for x in best_fit_X
                                  for y in best_fit_Y
                                  ] for z in ql_X])
    best_fit_qout = np.array([fitfunc_3d(fit_res.params, x)
                              for x in best_fit_Domain])
    ql_Y = np.sum(best_fit_qout, axis=1) * norm_scale_factor
    assert ql_X.shape == ql_Y.shape



    qlong = hist_3d.ratio._ptr.ProjectionZ("qlong", xmin, xmax-1, ymin, ymax-1)
    qlong.SetStats(False)
    qlong.SetTitle("Q_{long};; CF(q_{long})")
    qlong.Scale(norm_scale_factor)
    qlong.Write()

    if do_rebin:
        qlong.Rebin(2)
        qlong.Scale(1.0/2.0)

    ql_graph = ROOT.TGraph(len(ql_Y), ql_X, ql_Y)
    ql_graph.SetLineColor(2)

    output_canvas = ROOT.TCanvas("output")
    output_canvas.Divide(1, 3, 0, 0)
    for i, p in enumerate([(qout, qo_graph), (qside, qs_graph), (qlong, ql_graph)]):
        output_canvas.cd(i + 1)
        p[0].Draw()
        p[1].Draw("same")

    output_canvas.Draw()
    output_canvas.SaveAs(analysis_name + "_q3d.png")
    # output_image = ROOT.TImage.Create()
    # output_image.FromPad(output_canvas)
    # output_image.WriteImage(analysis_name + "_q3d.png")

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

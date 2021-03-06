#!/usr/bin/env python3
#
# post_analysis/3d_fit.py
#
from __future__ import print_function, absolute_import

import sys
import time
import types
import ctypes
import numbers
import itertools
import numpy as np
import matplotlib as ml
import matplotlib.pyplot as plt

from pprint import pprint
from stumpy import Histogram
from argparse import ArgumentParser
from collections import defaultdict
from fitting.gaussian import GaussianModel, GaussianModelCoulomb
from pionpion import Femtolist, Analysis
from pionpion.root_helpers import get_root_object
from pionpion.q3d import Q3D
from pionpion.fit import (
    fitfunc_qinv,
    fitfunc_3d,
)

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

print("Done (%fs)" % (time.monotonic() - TSTART), file=sys.stderr)

CACHE = []
STORED_CANVASES = []

NUM_QINV_PATH = "Num_qinv_pip Num_qinv_pim Numc_qinv_pip Numc_qinv_pim".split()
DEN_QINV_PATH = "Den_qinv_pip Den_qinv_pim Denc_qinv_pip Denc_qinv_pim".split()
NUM_Q3D_PATH = ["Num_q3D_pip", "Num_q3D_pim"]
DEN_Q3D_PATH = ["Den_q3D_pip", "Den_q3D_pim"]


def arguments():
    """Parse and return command line arguments"""
    parser = ArgumentParser()
    parser.add_argument("filename", help="root filename to analyze")
    parser.add_argument("output",
                        nargs='?',
                        default=None,
                        help="Root filename to write results")
    return parser.parse_args()


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


def hist_method_to_array(hist, func):
    nbins = hist.GetNbinsX()
    func = getattr(hist, func)
    return np.array(list(map(func, range(1, nbins))))


def get_ratio(name, num, den, norm_x_ranges, cache=True):
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


args = arguments()

# file = TFile(args.filename, 'READ')
# femtolist = get_root_object(file, ['femtolist', 'PWG2FEMTO.femtolist'])
femtolist = Femtolist(args.filename)


if femtolist == None:
    print("Could not find femtolist", file=sys.stderr)
    sys.exit(1)


if args.output is not None:
    output = TFile(args.output, 'RECREATE')
else:
    # just make a mock object so no output is created
    output_filename = args.filename.rstrip(".root") + ".q3d.root"
    output = TFile(output_filename, "RECREATE")
    # import unittest.mock
    # output = unittest.mock.MagicMock()


TRACK_CUT_INFO_STR = """\
 Charge: {charge}
 Mass: {mass}
 Pt: {pt[minimum]} -> {pt[maximum]}
"""


def do_qinv_analysis(num, den, cf_title="CF; q (GeV); CF(q)", output_imagename='qinv.eps'):
    """
    Code performing the qinv analysis - should probably be moved to a submodule

    Args
    ----
    num : Histogram
        Numerator histogram
    den : Histogram
        Denominator histogram
    """

    ModelClass = GaussianModelCoulomb

    fit_slice = num.x_axis.get_slice((0, 0.17))
    qinv_params = ModelClass.guess()
    x = num.x_axis.bin_centers[fit_slice]


    num_slice, den_slice = num[fit_slice], den[fit_slice]

    TIMESTART = time.monotonic()

    # use log-likelihood fitting method
    # qinv_fit = minimize(GaussianModel.as_loglike, qinv_params, args=(x, num_slice, den_slice), method='differential_evolution')

    # use old 'simple' residual method
    ratio = num / den
    ratio, errors = ratio[fit_slice], ratio.errors[fit_slice]
    assert ratio.shape == errors.shape, 'Shapes do not match (%s ≠ %s)' % (ratio.shape, errors.shape) # '({ratio.shape} ≠ {errors.shape})'
    # qinv_fit = minimize(ModelClass.as_resid, qinv_params, args=(x, ratio, errors))

    # random data to check chi^2
    # rdata = GaussianMSodel().eval(qinv_params, x=x)
    # offset = np.random.normal(0, 0.01, len(rdata))
    # rdata += offset + 0.001
    # errors = np.abs(offset)  # np.random.normal(0, 0.01, len(rdata))
    # ratio = rdata
    # qinv_fit = minimize(GaussianModel.as_resid, qinv_params, args=(x, rdata, errors))

    TIME_DELTA = time.monotonic() - TIMESTART
    report_fit(qinv_fit)
    print("fitting time %0.3fs (%0.3f ms/call)" % (TIME_DELTA, TIME_DELTA * 1e3 / qinv_fit.nfev))

    # generate x values for fit plots
    FIT_X = np.linspace(x[0], x[-1], 300)
    FIT_Y = ModelClass().eval(qinv_fit.params, x=FIT_X)

    # Repeat without Coulomb interaction
    qinv_fit_nocoulomb = minimize(GaussianModel.as_resid, qinv_params, args=(x, ratio, errors))
    report_fit(qinv_fit_nocoulomb)
    FIT_Y_NO_COULOMB = GaussianModel().eval(qinv_fit_nocoulomb.params, x=FIT_X)

    # print(np.array([FIT_Y, ratio[fit_slice], ratio.errors[fit_slice]]).T)

    plt.plot(FIT_X, FIT_Y)
    plt.plot(FIT_X, FIT_Y_NO_COULOMB)
    plt.errorbar(x, ratio, errors, fmt='.')
    plt.show()

    return None
    FIT_Y = fitfunc_qinv(qinv_fit.params, FIT_X)

    NOCOULOMB = GaussianModel
    canvas_qinv = gen_canvas()
    # canvas_qinv.cd(1)
    ratio.GetXaxis().SetRangeUser(0.0, 0.5)
    ratio.GetYaxis().SetTitleOffset(1.2)
    ratio.Draw()

    fit_plot = TGraph(len(FIT_X), FIT_X, FIT_Y)
    CACHE.append(fit_plot)

    fit_plot.SetLineColor(2)
    fit_plot.Draw("same")
    # canvas_qinv.Draw()
    canvas_qinv.SaveAs(output_imagename)
    canvas_qinv.Write()
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
    if True:
        # num, dern = analysis.qinv_pair
        n = get_root_object(analysis._data, analysis.QINV_NUM_PATH)
        if n == None:
            print("Error! Could not load numerator in analysis")
            continue
        num = Histogram.BuildFromRootHist(n)

        d = get_root_object(analysis._data, analysis.QINV_DEN_PATH)
        if d == None:
            print("Error! Could not load denominator in analysis")
            continue
        den = Histogram.BuildFromRootHist(d)

        if num == None or den == None:
            print("Missing Qinv plots")
            print('  num:', num)
            print('  den:', den)
        else:
            print(" ***** Q_inv Study *****\n")
            qinv_title = make_cf_title(title='Q_{inv}', units='q_{inv}')
            do_qinv_analysis(num, den, cf_title=qinv_title, output_imagename=analysis_name + '_qinv.eps')

    #
    # Fake Qinv - Kt binned
    #
    # fake_qinv_num = get_root_object(analysis, ["fakeNum_q3D_pip"])
    # fake_qinv_den = get_root_object(analysis, ["FakeDen_q3D_pip"])
    # if fake_qinv_num == None or fake_qinv_den == None:
    #     print("Missing fake_qinv", fake_qinv_num, fake_qinv_den)
    # else:
    #     print("\n\n")
    #     print(" ***** Fake Q_inv Study *****\n")
    #     do_qinv_analysis(fake_qinv_num, fake_qinv_den,
    #                      cf_title="Fake Q_inv; q_{inv} (fake); C(q_{inv});",
    #                      output_imagename=analysis_name + '_fake_qinv.png')

    #
    # Qinv - Kt binned
    #
    if False:
        kt_qinv = get_root_object(analysis, ["KT_Qinv"])
        if kt_qinv != None:
            print("   Found kt binned Qinv")
            for ktbin in kt_qinv:
                kt_bin_name = ktbin.GetName()
                print("       (%s)" % kt_bin_name, NUM_QINV_PATH)
                ktn_root = get_root_object(ktbin, NUM_QINV_PATH)
                if ktn_root == None:
                    print("Could not find numerator")
                    continue
                ktn = Histogram.BuildFromRootHist(ktn_root)
                ktd_root = get_root_object(ktbin, DEN_QINV_PATH)
                if ktd_root == None:
                    print("Could not find denominator")
                    continue
                ktd = Histogram.BuildFromRootHist(ktd_root)
                do_qinv_analysis(ktn, ktd,
                                cf_title="KT %s Q_inv; q_{inv} (fake); C(q_{inv});" % (kt_bin_name),
                                output_imagename=analysis_name + '_fake_qinv.png')

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
    q3d_params.add('lam', value=0.5)
    q3d_params.add('norm', value=1.0, min=0.0)



    hist_3d = Q3D(q3d_num, q3d_den)

    domains_ranges = (-0.01, 0.01), (-0.01, 0.01), (-0.0, 0.007) #1, 0.01)
    # domains_ranges = (-.09, 0.09), (-.09, 0.09), (-.09, 0.09)
    xx, yy, zz = np.meshgrid(*(a.bin_centers for a in hist_3d.num.axes))
    q_domain = np.stack([xx.flatten(), yy.flatten(), zz.flatten()]).T
    ratio = hist_3d.ratio.data.flatten()
    ratio_err = hist_3d.ratio.errors.flatten()
    print('q_domain', q_domain.shape, 'ratio', ratio.shape, ratio_err.shape)

    # domains_ranges = (1, -2), (1, -2), (1, -1)
    # slices = hist_3d.num.get_slice(*domains_ranges)
    # slices = slice(None), slice(None), slice(None)
    # fitfunc_3d(q3d_params, q_domain, (ratio, ratio_err))
    print("------")
    t = time.monotonic()
    TIMESTART = time.monotonic()
    fit_res = minimize(fitfunc_3d, q3d_params, args=(q_domain, (ratio, ratio_err)))
    print(":::::", fit_res)
    TIME_DELTA = time.monotonic() - TIMESTART
    report_fit(fit_res)
    print("fitting time %0.3fs (%0.3f ms/call)" % (TIME_DELTA, TIME_DELTA * 1e3 / fit_res.nfev))

    fit_domain = q_domain
    best_fit = fitfunc_3d(fit_res.params, fit_domain).reshape(hist_3d.num.shape)

    # slices
    s = hist_3d.num.get_slice(*domains_ranges)

    x_width = s[0].stop - s[0].start
    y_width = s[1].stop - s[1].start
    z_width = s[2].stop - s[2].start
    print(':>', x_width, y_width, z_width)
    # x_width = y_width = z_width = 1.8 # 0.05 + 0.05 # hist_3d.num.x_axis[-0.05]

    print(">>", s)

    qout = hist_3d.projection_out(y_slice=domains_ranges[1], z_slice=domains_ranges[2]) # / y_width / z_width / fit_res.params['norm']
    qout_err = hist_3d.projection_out_error(y_slice=domains_ranges[1], z_slice=domains_ranges[2]) # / y_width / z_width
    fit_qout = best_fit[:, s[1], s[2]].sum(axis=(1, 2)) / y_width / z_width # / fit_res.params['norm']

    qside = hist_3d.projection_side(x_slice=domains_ranges[0], z_slice=domains_ranges[2]) / x_width / z_width
    qside_err = hist_3d.projection_side_error(*domains_ranges[:2])
    fit_qside = best_fit[s[0], :, s[2]].sum(axis=(0, 2)) / x_width / z_width

    qlong = hist_3d.projection_long(x_slice=domains_ranges[0], y_slice=domains_ranges[1])
    qlong_err = hist_3d.projection_long_error(*domains_ranges[:2])
    fit_qlong = best_fit[s[0], s[1], :].sum(axis=(0, 1)) / x_width / y_width

    f, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2) # , sharex='col', sharey='row')

    qout_xaxis = hist_3d.ratio.x_axis.bin_centers
    print(qout.shape, qout_err.shape, qout_xaxis.shape)
    ax1.errorbar(qout_xaxis, qout, fmt='.', yerr=qout_err)
    # ax1.plot(qout_xaxis, fit_qout)
    ax1.set_title('Qout')

    qside_xaxis = hist_3d.ratio.y_axis.bin_centers
    ax2.errorbar(qside_xaxis, qside, fmt='.', yerr=qside_err)
    ax2.plot(qside_xaxis, fit_qlong)
    ax2.set_title('Qside')

    qlong_xaxis = hist_3d.ratio.z_axis.bin_centers
    # ax3.errorbar(qlong_xaxis, qlong, fmt='.', yerr=qlong_err)
    ax3.plot(qlong_xaxis, fit_qlong)
    ax3.set_title('Qlong')

    ax4.set_axis_off()
    ax4.text(0.2, 0.5,
        '$R_{{out}}$: {r_out.value:03f} ≠ {r_out.stderr:.03f}\n'
        '$R_{{side}}$: {r_side.value:03f}\n'
        '$R_{{long}}$: {r_long.value:03f}\n'
        '\n'
        '$\lambda$: {lam.value:03f}\n'
        '$norm$: {norm.value:03f}\n'.format(
            **fit_res.params),
        fontsize=20,
        horizontalalignment='left',
        verticalalignment='center',
        transform=ax4.transAxes)

    ax4.text(0.5, 0.0, 'run2, 0-5% centrality')
    # ax4.text(3, 8, 'boxed italics text in data coords', style='italic',
    #     bbox={'facecolor':'red', 'alpha':0.5, 'pad':10})
    # ax3.scatter(x, 2 * y ** 2 - 1, color='r')
    # ax4.plot(x, 2 * y ** 2 - 1, color='r')
    plt.tight_layout()
    plt.show()
    # plt.figure()
    #
    # plt.
    # plt.
    # plt.show()

    qlong = hist_3d.projection_long(*domains_ranges[:2])
    # print(qlong)


    kt_binned = analysis['KT_Q3D']
    for kt_bin in kt_binned:
        kt_bin_name = kt_bin.GetName()
        print(':::::', kt_bin_name)
        q3d_num = get_root_object(kt_bin, NUM_Q3D_PATH)
        q3d_den = get_root_object(kt_bin, DEN_Q3D_PATH)
        if q3d_num == None or q3d_den == None:
            print("  Could not find num/den pair")
            continue
        hist_3d = Q3D(q3d_num, q3d_den)

        fit_res = minimize(fitfunc_3d, q3d_params, args=(q_domain, (ratio, ratio_err)))

        domains_ranges = (-.05, 0.05), (-.05, 0.05), (-.05, 0.05)
        xx, yy, zz = np.meshgrid(*(hist_3d.num.axes[i].bin_centers for i in range(3)))
        q_domain = np.stack([xx.flatten(), yy.flatten(), zz.flatten()]).T
        ratio = hist_3d.ratio.data.flatten()
        ratio_err = hist_3d.ratio.errors.flatten()

    continue

    # hist_3d.ratio._ptr.Write()
    out_side_num, out_side_den = hist_3d.num._ptr, hist_3d.den._ptr

    zz = hist_3d.ratio._ptr.GetZaxis().FindBin(0.0)


    for zdist in range(1, 4):
        zrange = zz - zdist, zz + zdist
        out_side_num.GetZaxis().SetRange(*zrange)
        out_side_den.GetZaxis().SetRange(*zrange)

        out_side = out_side_num.Project3D("yx")
        out_side.Divide(out_side_den.Project3D("yx"))
        print(":::out_side: %s" % out_side)

        # out_side_cnvs = ROOT.TCanvas("out_side")
        # out_side.SetStats(False)
        # out_side.Draw("colz")
        # out_side_cnvs.Draw()
        # out_side_cnvs.SaveAs("OUTSIDEz%02d.eps" % zdist)
        out_side.Write()

        # input()
    out_side_num.GetZaxis().SetRange()
    out_side_den.GetZaxis().SetRange()
    # out_side_num = hist_3d.num.project_2d(0, 1, (-0.03, 0.03), bounds_x=(0.0, None))
    # out_side_den = hist_3d.den.project_2d(0, 1, (-0.03, 0.03), bounds_x=(0.0, None))
    # # print(out_side_num.shape)
    # out_side_ratio = out_side_num / out_side_den
    # out_side = root_numpy.array2hist(out_side_ratio, hist_3d.num._ptr.Clone("out_side"))
    # print(out_side)
    # print(hist_3d.ratio.data, out_side_ratio)
    # print(hist_3d.ratio.data - out_side_ratio)
    # out_side = hist_3d.ratio.project_2d(0, 1, (-0.03, 0.03), bounds_x=(0.0, None))

    # fig = plt.figure(figsize=(6, 3.2))

    # ax = fig.add_subplot(111)
    # ax.set_title('colorMap')
    # plt.contourf(out_side)
    # ax.set_aspect('equal')

    # cax = fig.add_axes([0.12, 0.1, 0.78, 0.8])
    # cax.get_xaxis().set_visible(True)
    # cax.get_yaxis().set_visible(False)
    # cax.patch.set_alpha(0)
    # cax.set_frame_on(False)
    # plt.colorbar(orientation='vertical')
    # plt.show()


    # domains_ranges = (-0.2, 0.2), (-0.2, 0.2), (-0.2, 0.2)
    domains_ranges = (2, -2), (2, -2), (2, -2)
    # domains_ranges = (1, -2), (1, -2), (1, -1)
    slices = hist_3d.num.get_slice(*domains_ranges)
    # slices = slice(None), slice(None), slice(None)

    t = time.monotonic()
    dom = hist_3d.num.bounded_domain(*slices)

    # mask so that only bins with non-zero errors are chosen
    # print(slices)
    # print(hist_3d.ratio.shape, hist_3d.ratio.errors.shape)
    # print(hist_3d.ratio)
    # print(hist_3d.ratio.errors)
    # print("----")
    ratio_err = hist_3d.ratio.errors[slices].flatten()
    error_mask = ratio_err != 0
    dom = dom[error_mask]
    ratio_err = ratio_err[error_mask]
    ratio = hist_3d.ratio_data[slices].flatten()[error_mask]

    TIMESTART = time.monotonic()
    fit_res = minimize(fitfunc_3d, q3d_params, args=(dom, (ratio, ratio_err)))
    print(":::::", fit_res)
    TIME_DELTA = time.monotonic() - TIMESTART
    report_fit(fit_res)
    print("fitting time %0.3fss (%0.3f ms/call)" % (TIME_DELTA, TIME_DELTA * 1e3 / fit_res.nfev))
    # projection_bins = hist_3d.num.bin_ranges([-0.01, 0.01], [-0.01, 0.01], [-0.01, 0.01])
    # xmin, xmax, ymin, ymax, zmin, zmax = [x for x in projection_bins for x in x]
    # cr = (0.0, 2)
    print("~~~", hist_3d.num.get_slice(0.0))
    cr = (-0.1, 0.1, 0.0)
    xmin_xmax = hist_3d.num.get_slice(*cr)

    # xmin, xmax, ymin, ymax, zmin, zmax = hist_3d.num.centered_bin_ranges(cr, cr, cr, expand=True, inclusive=True)
    xmin, xmax, ymin, ymax, zmin, zmax = 34, 38, 34, 38, 34, 38,
    # hist_3d.ratio._ptr.Scale(1.0 / fit_res.params['norm'])
    # hist_3d.ratio_data = hist_3d.ratio_data / fit_res.params['norm']

    out_side_cnvs = ROOT.TCanvas("out_side")
    print('>>>>', out_side_cnvs)
    zz = hist_3d.ratio._ptr.GetZaxis().FindBin(0.0)
    zdist = 3
    hist_3d.ratio._ptr.GetZaxis().SetRange(zz - zdist, zz + zdist)
    # hist_3d.ratio._ptr.GetZaxis().SetRange(zmin, zmax)
    out_side = hist_3d.ratio._ptr.Project3D("yx")
    out_side.Write()
    out_side.SetStats(False)
    # out_side.Draw("colz")
    # out_side_cnvs.Draw()
    # out_side_cnvs.SaveAs("OUTSIDEz0.png")
    # hist_3d.ratio._ptr.GetZaxis().SetRange()

    do_rebin = False

    print('XXXXXXXX', "qout", ymin, ymax-1, zmin, zmax-1)
    # qout = hist_3d.ratio.projection_out()
    qout = hist_3d.projection_out()
    # qout = hist_3d.ratio._ptr.ProjectionX("qout", ymin, ymax-1, zmin, zmax-1)
    # qout.SetStats(False)
    # qout
    # qout.GetYaxis().SetTitleSize(0.06)
    # qout.GetYaxis().SetTitleOffset(0.6)

    # qout.Write()
    norm_scale_factor = 1.0 / ((ymax - ymin) * (zmax - zmin)) / fit_res.params['norm']
    # qout.Scale(norm_scale_factor)
    qout /= norm_scale_factor


    if do_rebin:
        qout.Rebin(2)
        qout.Scale(.5)

    # qout.SetTitle("q_{out};; CF(q_{out})")
    best_fit_X = hist_3d.ratio.x_axis[xmin:xmax]
    best_fit_Y = hist_3d.ratio.y_axis[ymin:ymax]
    best_fit_Z = hist_3d.ratio.z_axis[zmin:zmax]
    print(best_fit_X , best_fit_Y, best_fit_Z)

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
    qside.SetTitle("q_{side};; CF(q_{side})")
    # qside.Write()

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
    qlong.SetTitle("q_{long};; CF(q_{long})")
    qlong.Scale(norm_scale_factor)
    # qlong.Write()

    if do_rebin:
        qlong.Rebin(2)
        qlong.Scale(1.0/2.0)

    ql_graph = ROOT.TGraph(len(ql_Y), ql_X, ql_Y)
    ql_graph.SetLineColor(2)

    output_canvas = ROOT.TCanvas("output")
    output_canvas.Divide(1, 3, 0, 0)
    # for i, p in enumerate([(qout, qo_graph), (qside, qs_graph), (qlong, ql_graph)]):
    #     output_canvas.cd(i + 1)
    #     p[0].Draw()
    #     p[1].Draw("same")

    # output_canvas.Draw()
    output_canvas.SaveAs(analysis_name + "_q3d.eps")
    # output_image = ROOT.TImage.Create()
    # output_image.FromPad(output_canvas)
    # output_image.WriteImage(analysis_name + "_q3d.png")

    # input()

    # ROOT.gApplication.Run()

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

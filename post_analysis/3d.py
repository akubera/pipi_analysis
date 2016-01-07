#!/usr/bin/env python3
#
# post_analysis/3d.py
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
from pionpion.root_helpers import get_root_object
from hist_helpers import bin_range as BinRange
import ROOT
from ROOT import (
    TFile,
    TMinuit,
)


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


def get_3d_ratio(name, num, den, norm_x=None, norm_y=None, norm_z=None, *, cache=True):
    """
    Get the ratio of a 3D histogram
    """

    # norm_x, norm_y, norm_z = map(
    # *norm_r, = map(
    #     lambda r: r[0] if not isinstance(r[0], numbers.Number) else r,
    #     (norm_x, norm_y, norm_z)
    # )
    # # Get the 'find bins' methods in cartesian order
    # n_findbins, d_findbins = map(
    #     lambda a: (a.GetXaxis().FindBin, a.GetYaxis().FindBin, a.GetZaxis().FindBin),
    #     (num, den)
    # )
    # # creates a list of
    # l = [a for q, f in zip(norm_r, n_findbins) for a in map(f, q)]
    # num_scale = num.Integral(*l)
    #
    # l = [a for q, f in zip(norm_r, d_findbins) for a in map(f, q)]
    # den_scale = den.Integral(*l)

    ratio = num.Clone(name)
    # ratio.Divide(num, den, 1.0 / num_scale, 1.0 / den_scale)
    ratio.Divide(num, den)
    ratio.SetStats(False)

    return ratio


for analysis in femtolist:

    analysis_name = analysis.GetName()

    output.mkdir(analysis_name)
    output.cd(analysis_name)

    q3d_num = get_root_object(analysis, ["Num_q3D_pip", "Num_q3D_pim"])
    q3d_den = get_root_object(analysis, ["Den_q3D_pip", "Den_q3D_pim"])

    ratio = get_3d_ratio('ratio', q3d_num, q3d_den) # , (.4, .7), (.4, .7), (.5, 0.9))

    def yes(_): return True

    def bin_range(hist, x_filt=yes, y_filt=yes, z_filt=yes):
        for x in range(1, hist.GetNbinsX() + 1):
            if not x_filt(x): continue
            for y in range(1, hist.GetNbinsY() + 1):
                if not y_filt(y): continue
                for z in range(1, hist.GetNbinsZ() + 1):
                    if not z_filt(z): continue
                    if hist.GetBinContent(x, y, z) == 0: continue
                    yield x, y, z

    def bin_centers(hist, bin_gen=None):
        if bin_gen is None:
            bin_gen = partial(bin_range, hist, yes, yes, yes)
        xcenter = hist.GetXaxis().GetBinCenter
        ycenter = hist.GetYaxis().GetBinCenter
        zcenter = hist.GetZaxis().GetBinCenter
        for x, y, z in bin_gen():
            yield xcenter(x), ycenter(y), zcenter(z)


    def filter_between(*r):
        return lambda v: r[0] <= v <= r[1]

    print("loading", analysis_name, end=' ', flush=True)

    TIMESTART = time.monotonic()
    bg = partial(bin_range, ratio)
    X = np.array(list(bin_centers(ratio, bg))).T
    Y = np.array(list(apply(ratio.GetBinContent, bg())))
    E = np.array(list(apply(ratio.GetBinError, bg())))
    TIMESTOP = time.monotonic()
    print("(time %0.3fs)" % (TIMESTOP - TIMESTART))

    project_xy = defaultdict(float)

    for x, y in zip(X.T, Y):
        project_xy[(x[0], x[1])] += y

    q3d_params = Parameters()
    q3d_params.add('r_out', value=1.0, min=0.0)
    q3d_params.add('r_side', value=1.0, min=0.0)
    q3d_params.add('r_long', value=1.0, min=0.0)
    q3d_params.add('lam', value=0.5)
    q3d_params.add('norm', value=1.0, min=0.0)

    iii = 0

    def model_3d(params, x, y=None):
        global iii
        iii += 1

        norm = params['norm'].value
        lam = params['lam'].value
        r_out = params['r_out'].value
        r_long = params['r_long'].value
        r_side = params['r_side'].value

        p = np.array([r_out, r_side, r_long]) / 0.197

        if np.shape(x)[1] == 3:
            t = (p * x) ** 2
        else:
            t = (p * x.T) ** 2
        t = np.sum(t, axis=1)

        model = norm * (1 + lam * np.exp(-t))

        if y is None:
            return model

        data, err = y[0], y[1]

        res = np.sqrt((model - data) ** 2 / err ** 2)

        return res


    TIMESTART = time.monotonic()
    fit_res = minimize(model_3d, q3d_params, args=(X, (Y, E)))
    TIMESTOP = time.monotonic()
    print("fitting time %0.3fs, %d iterations" % (TIMESTOP - TIMESTART, iii))
    report_fit(fit_res)

    xzero = ratio.GetXaxis().FindBin(0.0)
    yzero = ratio.GetYaxis().FindBin(0.0)
    zzero = ratio.GetZaxis().FindBin(0.0)

    bin_sep = 1
    xmin, xmax = xzero - bin_sep, xzero + bin_sep + 1
    ymin, ymax = yzero - bin_sep, yzero + bin_sep + 1
    zmin, zmax = zzero - bin_sep, zzero + bin_sep + 1

    xspace = np.linspace(-0.6, 0.6, 400)
    yspace = tuple(map(ratio.GetYaxis().GetBinCenter, range(ymin, ymax+1)))
    zspace = tuple(map(ratio.GetZaxis().GetBinCenter, range(zmin, zmax+1)))

    qo_binrange = BinRange(ratio,
                           y_bin_range=(ymin, ymax),
                           z_bin_range=(zmin, zmax),
                           filter_zero_bins=False)
    qo_bins = defaultdict(list)
    for r in qo_binrange:
        qo_bins[r[0]].append(r)

    # qo_domain = np.array(list(tuple(bin_centers(ratio, lambda: qo_x_bins))
    #                           for qo_x_bins in qo_bins.values()))

    qo_domain = np.array([[[x, y, z] for y in yspace for z in zspace]
                          for x in xspace])
    qo_y = np.array(list(model_3d(fit_res.params, x) for x in qo_domain))

    # cqout = ROOT.TCanvas("cqout")
    qout = ratio.ProjectionX("qout", ymin, ymax, zmin, zmax)
    # qo_X = np.array(list(qout.GetBinCenter(i) for i in range(qout.GetXaxis().GetNbins())))
    qo_X = xspace
    qo_Y = np.sum(qo_y, axis=1)

    qo_graph = ROOT.TGraph(len(qo_X), qo_X, qo_Y)
    qout.Draw()

    # cqout_g = ROOT.TCanvas("cqout graph")
    qo_graph.SetLineColor(2)
    qo_graph.Draw("same")

    input()


    qs_binrange = BinRange(ratio,
                           x_bin_range=(xmin, xmax),
                           z_bin_range=(zmin, zmax),
                           filter_zero_bins=False)
    qs_bins = defaultdict(list)
    for r in qs_binrange:
        qs_bins[r[0]].append(r)

    qs_domain = np.array(list(tuple(bin_centers(ratio, lambda: qs_x_bins))
                              for qs_x_bins in qs_bins.values()))
    # for i in qo_domain:
    #     print(i)
    qs_y = np.array(list(model_3d(fit_res.params, x) for x in qo_domain))
    # print("qo_y:", qo_y)

    qside_canvas = ROOT.TCanvas("qside_canvas")
    qside = ratio.ProjectionY("qside", xmin, xmax, zmin, zmax)
    qs_X = np.array(list(qside.GetBinCenter(i) for i in range(qside.GetXaxis().GetNbins())))
    qs_Y = np.sum(qs_y, axis=1)

    qs_graph = ROOT.TGraph(len(qs_X), qs_X, qs_Y)
    qside.Draw()

    qs_graph.SetLineColor(2)
    qs_graph.Draw("same")




    # def get_projected_axis(name, func, slice1, slice2, axis):
    #     q = func(name, *slice1, *slice2)
    #     qx = np.array(list(q.GetBinCenter(i) for i in range(axis.GetNbins())))
    #     qsx = np.array(list(map(qside.GetBinCenter, range(axis.GetNbins()))))
    #
    # y_proj = ratio.ProjectionY("qside", xmin, xmax, zmin, zmax)
    # qside = get_projected_axis("qside")









    ql_binrange = BinRange(ratio,
                           x_bin_range=(xmin, xmax),
                           z_bin_range=(zmin, zmax),
                           filter_zero_bins=False)
    ql_bins = defaultdict(list)
    for r in ql_binrange:
        ql_bins[r[0]].append(r)

    ql_domain = np.array(list(tuple(bin_centers(ratio, lambda: ql_x_bins))
                              for ql_x_bins in ql_bins.values()))
    # for i in qo_domain:
    #     print(i)
    ql_y = np.array(list(model_3d(fit_res.params, x) for x in qo_domain))
    # print("qo_y:", qo_y)

    qlong_canvas = ROOT.TCanvas("qlong_canvas")
    qlong = ratio.ProjectionZ("qlong", xmin, xmax, ymin, ymax)
    ql_X = np.array(list(qlong.GetBinCenter(i) for i in range(qlong.GetXaxis().GetNbins())))
    ql_Y = np.sum(ql_y, axis=1)

    ql_graph = ROOT.TGraph(len(ql_X), ql_X, ql_Y)
    qlong.Draw()

    ql_graph.SetLineColor(2)
    ql_graph.Draw("same")







    # coutside = ROOT.TCanvas("out_side")
    # ratio.GetZaxis().SetRangeUser(-0.05, 0.05)
    # out_side = ratio.Project3D("xy")
    # out_side.Draw("surf3")



    # ratio.Draw()

    # print('PROJECT', min(project_xy.keys()), max(project_xy.keys()))
    # themin = [1e4, 1e4]
    # themax = [-1e4, -1e4]
    # for k in project_xy.keys():
    #     if themin[0] > k[0]:
    #         themin[0] = k[0]
    #     elif themax[0] < k[0]:
    #         themax[0] = k[0]
    #
    #     if themin[1] > k[1]:
    #         themin[1] = k[1]
    #     elif themax[1] < k[1]:
    #         themax[1] = k[1]
    # print("MIN:", themin)
    # print("MAX:", themax)

    # for xy, v in project_xy.items():
    #     x, y = xy
    #     dataframe

    # X = np.array(list(bin_centers(ratio)).T

    input()

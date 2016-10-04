#!/usr/bin/env python3
#
# Compare things with others
#
import sys
import ROOT
import numpy as np
# from ROOT import *
from pathlib import Path
from os.path import dirname
# from
# from rootpy.interactive import wait
# from rootpy.plotting import F1, Hist, HistStack, Graph, Canvas, set_style


DATA_PATH = (Path(dirname(__file__)) / '../data').resolve()

pion_cf = ROOT.TFile(str(DATA_PATH / 'pions' / 'PionsCF.root'), 'READ')
my_data = ROOT.TFile(str(DATA_PATH / '2016-06-08.a.qinv.root'), 'READ')
# my_data = ROOT.TFile(sys.argv[1], "READ")

def walk_root_object(obj):
    if isinstance(obj, ROOT.TDirectory):
        for key in obj.GetListOfKeys():
            yield from walk_root_object(key.ReadObj())
    elif isinstance(obj, (ROOT.TList, ROOT.TObjArray)):
        for o in obj:
            yield from walk_root_object(o)
    else:
        yield obj

def filter_root_iterator(name, obj):
    for o in walk_root_object(obj):
        if o.GetName() == name:
            yield o

data = np.array([[
                [a.GetX()[i], a.GetY()[i], a.GetErrorY(i)]
                for i in range(a.GetN())]
                for a in list(filter_root_iterator('radius', my_data))]).T

x = np.copy(np.sqrt(data[0].T[0] ** 2 + 0.139 ** 2))
y = np.copy(data[1].mean(axis=1))
ye = np.copy(np.sqrt(np.mean(data[2] ** 2, axis=1)))
# print(x, y, ye)


radius_canvas = ROOT.TCanvas("radius_canvas")

a = ROOT.TGraphErrors(len(x), x, y, np.zeros(len(x)), ye)
a.SetTitle("Radius; <m_{T}> GeV; R_{inv}")
a.SetMarkerColor(2)
a.SetLineColor(2)
a.SetMarkerStyle(20)
a.SetMarkerSize(1)
a.Draw("AP")

numpoints = 7
xerr = np.zeros(numpoints)
xval = np.array([0.287195, 0.375873, 0.469237, 0.565494, 0.66286, 0.759927, 0.877914])
yval = np.array([8.98, 8.385, 7.775, 7.275, 6.675, 6.295, 5.825])
yerr = np.array([0.06, 0.09, 0.08, 0.105, 0.095, 0.115, 0.11])
p9053_d32x1y1 = ROOT.TGraphErrors(numpoints, xval, yval, xerr, yerr)
p9053_d32x1y1.SetName("/HepData/9053/d32x1y1")
p9053_d32x1y1.SetLineColor(9)
p9053_d32x1y1.SetMarkerColor(9)
p9053_d32x1y1.SetMarkerStyle(20)
p9053_d32x1y1.SetMarkerSize(1)
p9053_d32x1y1.Draw("SAMEP")
leg = ROOT.TLegend(0.7, 0.7, 0.9, 0.9)
leg.AddEntry(a, "Kubera Analysis", "p")
leg.AddEntry(p9053_d32x1y1, "Paper", "p")
leg.Draw()
radius_canvas.Update()



lambda_canvas = ROOT.TCanvas("lambda_canvas")
yval = np.array([0.42, 0.41, 0.39, 0.36, 0.33, 0.29, 0.23])
yerr = np.array([0.01, 0.01, 0.01, 0.01, 0.015, 0.015, 0.01])
p9053_d32x1y1 = ROOT.TGraphErrors(numpoints, xval, yval, xerr, yerr)




data = np.array([[[a.GetX()[i], a.GetY()[i], a.GetErrorY(i)]
                  for i in range(a.GetN())]
                 for a in list(filter_root_iterator('lambda', my_data))]).T

x = np.copy(np.sqrt(data[0].T[0] ** 2 + 0.139 ** 2))
y = np.copy(data[1].mean(axis=1))
ye = np.copy(np.sqrt(np.mean(data[2] ** 2, axis=1)))

a = ROOT.TGraphErrors(len(x), x, y, np.zeros(len(x)), ye)
leg = ROOT.TLegend(0.7, 0.7, 0.9, 0.9)
leg.AddEntry(a, "Kubera Analysis", "p")
leg.AddEntry(p9053_d32x1y1, "Paper", "p")
a.SetTitle("Lambda Parameter; <m_{T}> GeV; #lambda")
a.SetMarkerColor(2)
a.SetLineColor(2)
a.SetMarkerStyle(20)
a.GetYaxis().SetRangeUser(0.2, 0.5)
a.Draw("AP")
p9053_d32x1y1.SetLineColor(9)
p9053_d32x1y1.SetMarkerColor(9)
p9053_d32x1y1.SetMarkerStyle(20)
p9053_d32x1y1.Draw("SAMEP")
leg.Draw()
lambda_canvas.Update()


ROOT.gApplication.Run(True)

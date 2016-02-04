#!/usr/bin/env python3.4
#
# post_analysis/presentation/track_plots.py
#
"""
Script which prints various track plots in given files.
"""

import sys
from argparse import ArgumentParser
from pionpion import Femtolist
import ROOT

parser = ArgumentParser()
parser.add_argument("--title-suffix",
                    type=str,
                    nargs='?',
                    default='',
                    help="Adds the words to the end of the histogram title")
parser.add_argument("root_filename", help="root filename to analyze")
parser.add_argument("--out",
                    dest="output_filename",
                    default=None,
                    type=str,
                    help="root filename to analyze")
args = parser.parse_args()

if args.output_filename is None:
    if args.root_filename.endswith('.root'):
        args.output_filename = args.root_filename[:-5] + ".track_plots.root"
    else:
        args.output_filename = args.root_filename + ".track_plots.root"

input_file = ROOT.TFile(args.root_filename, "READ")
if input_file.IsZombie():
    # print("Could not open root file '%s'" % (args.root_filename))
    sys.exit(1)

output = ROOT.TFile(args.output_filename, "RECREATE")

for analysis in Femtolist(input_file):
    # ROOT.gROOT.Reset()
    output.mkdir(analysis.name)
    output.cd(analysis.name)
    print("**", analysis.name)

    def get(path):
        return analysis['Tracks.pass.' + path]
    track_plots = analysis['Tracks']

    eta_pt = get('eta_Pt')
    print(" passing tracks:", eta_pt.GetEntries())

    pt = eta_pt.ProjectionY("pt")
    pt.SetTitle("p_{T} Distribution; p_{T} (GeV); N_{tracks};")
    pt.Write()

    get('PtPhi').Write()

    eta = eta_pt.ProjectionX("eta")
    eta.SetTitle("Pseudorapidity Distribution; #eta; N_{tracks};")
    eta.Write()

    get('EtaPhi').Write()
    eta_pt.Write()
    get('dEdX').Write()

    phi = get('EtaPhi').ProjectionX("phi")
    phi.Write()

    azimuth_canvas = ROOT.TCanvas("azimuth_canvas")
    cmd = """
    nbins = phi->GetNbinsX();
    theta = new Double_t[nbins];
    radius = new Double_t[nbins];
    errors = new Double_t[nbins];
    maximum = -1;
    for (int i = 0; i < nbins; i++) {
        // Double_t x = phi->GetBinCenter(i+1);
        // theta[i] = x >= 0 ? x : x + 2 * TMath::Pi();
        theta[i] = phi->GetBinCenter(i+1);
        radius[i] = phi->GetBinContent(i+1);
        errors[i] = phi->GetBinError(i+1);
        if (maximum < radius[i]) maximum = radius[i];
    }
    azimuth_plot = new TGraphPolar(nbins-1, theta, radius, 0, errors);
    azimuth_plot->SetTitle("Azimuthal Distribution");
    azimuth_plot->SetMarkerStyle(20);
    azimuth_plot->SetMarkerSize(0.7);
    azimuth_plot->SetMarkerColor(4);
    azimuth_plot->SetLineColor(2);
    azimuth_plot->SetLineWidth(3);
    azimuth_plot->Draw("PE");
    azimuth_canvas->Update(); // Call so GetPolargram works
    pg = azimuth_plot->GetPolargram();
    pg->SetNdivRadial(308);
    pg->SetNdivPolar(312);
    pg->SetRangeRadial(0.0, maximum * 1.2);
    azimuth_canvas->Update();
    delete[] theta;
    delete[] radius;
    delete[] errors;
    """
    tuple(map(ROOT.gROOT.ProcessLine, cmd.split("\n")))
    azimuth_canvas.Write()

# output.Write()
output.Close()

#!/usr/bin/env python

import ROOT
ROOT.gROOT.SetBatch()
ROOT.PyConfig.IgnoreCommandLineOptions = True
from pyroot_cms_scripts import CMS_style
import os
import argparse
ROOT.gErrorIgnoreLevel = ROOT.kError

parser = argparse.ArgumentParser()

parser.add_argument("-f", "--histfile")
parser.add_argument("-d", "--directory")
parser.add_argument("-a", "--variable")
parser.add_argument("-s", "--systematic")
parser.add_argument("-o", "--output", default="")

args = parser.parse_args()


canvas = ROOT.TCanvas("", "", 600, 600)
legend = ROOT.TLegend(0.6, 0.8, 0.89, 0.89)

root_file = ROOT.TFile.Open(f"{args.histfile}")
h_nom = root_file.Get(f"{args.directory}/{args.variable}")
h_Up = root_file.Get(f"{args.directory}_{args.systematic}Up/{args.variable}")
h_Down = root_file.Get(f"{args.directory}_{args.systematic}Down/{args.variable}")

if h_nom != None:
    h_nom.SetStats(0)
    h_nom.SetLineColor(ROOT.kBlue)
    legend.AddEntry(h_nom, "Nom", "l")

if h_Up != None:
    h_Up.SetStats(0)
    h_Up.SetBins(h_nom.GetNbinsX(), h_nom.GetXaxis().GetXmin(), h_nom.GetXaxis().GetXmax())
    h_Up.SetTitle(f"{h_nom.GetTitle()};{h_nom.GetXaxis().GetTitle()}")
    h_Up.SetLineColor(ROOT.kGreen)
    legend.AddEntry(h_Up, "Up", "l")

if h_Down != None:
    h_Down.SetStats(0)
    h_Down.SetBins(h_nom.GetNbinsX(), h_nom.GetXaxis().GetXmin(), h_nom.GetXaxis().GetXmax())
    h_Down.SetTitle(f"{h_nom.GetTitle()};{h_nom.GetXaxis().GetTitle()}")
    h_Down.SetLineColor(ROOT.kRed)
    legend.AddEntry(h_Down, "Down", "l")


ratio_plot = ROOT.TRatioPlot(h_Up, h_nom)
ratio_plot.SetSeparationMargin(0)
ratio_plot.SetH1DrawOpt("hist")
ratio_plot.SetH2DrawOpt("hist")
ratio_plot.Draw()

ratio_plot.GetLowerRefGraph().SetLineColor(h_Up.GetLineColor())
ratio_plot.GetLowerRefGraph().SetMinimum(0.0)
ratio_plot.GetLowerRefGraph().SetMaximum(1.5)
ratio_plot.GetLowYaxis().SetNdivisions(410)

lower_pad = ratio_plot.GetLowerPad()
upper_pad = ratio_plot.GetUpperPad()

lower_pad.cd()
h_Down_ratio = h_Down.Clone()
h_Down_ratio.Divide(h_nom)
h_Down_ratio.Draw("same")

upper_pad.cd()
h_Up.SetMaximum(1.5 * h_Up.GetMaximum())
h_Down.Draw("same hist")

legend.Draw()
canvas.Draw()

if args.output == "":
    out_dir = f"{args.histfile.replace('.root', '')}/{args.directory}"
    os.makedirs(out_dir, exist_ok=True)
    plot_filename = f"{out_dir}/{args.variable}_{args.systematic}"
    canvas.SaveAs(f"{plot_filename}.pdf")
    os.popen(f"convert -density 150 -antialias {plot_filename}.pdf -trim {plot_filename}.png 2> /dev/null")

else:
    canvas.SaveAs(args.output + ".pdf")
    os.popen(f"convert -density 150 -antialias {args.output}.pdf -trim {args.output}.png 2> /dev/null")

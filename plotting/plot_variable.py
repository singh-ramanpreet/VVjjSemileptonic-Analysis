#!/usr/bin/env python3

import sys
import argparse

parser = argparse.ArgumentParser()

parser.add_argument(
    "--hist_file", type=str, default="hists.root",
    help="histogram root file, default=%(default)s"
    )

parser.add_argument(
    "--variable", type=str, default="lept_pt1",
    help="name of the varaible, default=%(default)s"
    )

parser.add_argument(
    "--units", type=str, default="GeV",
    help="variable units, default=%(default)s"
    )

parser.add_argument(
    "--title_x", type=str, default="lept_{1} p_{T}",
    help="X axis title, default=%(default)s"
    )

parser.add_argument(
    "--title_y", type=str, default="",
    help="Y axis title, default=Events / (bw) (units)"
    )

parser.add_argument(
    "--show_bw", action="store_true",
    help="show bin width in Y axis title, default=%(default)s"
    )

parser.add_argument(
    "--leg_pos", type=float, nargs=4,
    default=[0.55, 0.65, 0.95, 0.9],
    help="legend position x1, y1, x2, y2, default=%(default)s"
    )

parser.add_argument(
    "--draw_with_ratio", action="store_true",
    help=", default=%(default)s"
    )

parser.add_argument(
    "--axis_max_digits", type=int, default=3,
    help=", default=%(default)s"
    )

parser.add_argument(
    "--log_y_axis", action="store_true",
    help=", default=%(default)s"
    )

parser.add_argument(
    "--scale_y_axis", type=float, default=1.2,
    help="1.2 means 20%% higher than maximum, default=%(default)s"
    )

parser.add_argument(
    "--lower_graph_title_y", type=str, default="#frac{Data}{MC}",
    help=", default=%(default)s"
    )

parser.add_argument(
    "--lower_graph_max_y", type=float, default=2.5,
    help=", default=%(default)s"
    )

parser.add_argument(
    "--lower_graph_min_y", type=float, default=-0.5,
    help=", default=%(default)s"
    )

parser.add_argument(
    "--lower_graph_ndivisions_y", type=int, default=404,
    help=", default=%(default)s"
    )

parser.add_argument(
    "--lower_graph_draw_opt", type=str, default="p",
    help=", default=%(default)s"
    )

parser.add_argument(
    "--plot_dir", type=str, default="plots",
    help=", default=%(default)s"
    )

parser.add_argument(
    "--batch_mode", action="store_true",
    help=", default=%(default)s"
    )


args = parser.parse_args()
import ROOT
from pyroot_cms_scripts import CMS_style, CMS_text

if args.batch_mode:
    ROOT.gROOT.SetBatch(True)

leg_pos_x1 = args.leg_pos[0]
leg_pos_y1 = args.leg_pos[1]
leg_pos_x2 = args.leg_pos[2]
leg_pos_y2 = args.leg_pos[3]

if args.units != "":
    args.title_x = f"{args.title_x} ({args.units})"

if args.title_y == "":
    args.title_y = "Events"
    
# Force CMS_style
# ==============
ROOT.TGaxis().SetMaxDigits(args.axis_max_digits)
CMS_style.SetLabelSize(0.042, "XYZ")
CMS_style.cd()
ROOT.gROOT.ForceStyle()

hist_file = ROOT.TFile.Open(args.hist_file)

# make stack of mc samples
# overlay data with points
# ========================
legend = ROOT.TLegend(leg_pos_x1, leg_pos_y1, leg_pos_x2, leg_pos_y2)
legend.SetFillStyle(0)
legend.SetBorderSize(0)
legend.SetTextFont(42)
legend.SetTextSize(0.03)
legend.SetNColumns(2)

h_dataM = hist_file.Get(f"dataM_{args.variable}")
h_dataE = hist_file.Get(f"dataE_{args.variable}")

h_data = h_dataM + h_dataE
legend.AddEntry(h_data, "Data", "pe")

bw = h_data.GetBinWidth(1)

if args.show_bw:
    args.title_y = f"{args.title_y} / {bw} {args.units}"

h_mc = ROOT.THStack("h_mc", f";{args.title_x};{args.title_y}")

h_Top = hist_file.Get(f"Top_{args.variable}")
h_Top.SetFillColor(ROOT.kYellow + 1)
h_Top.SetLineColor(ROOT.kYellow + 1)
h_Top.SetFillStyle(1001)
legend.AddEntry(h_Top, "Top", "f")

h_WJets = hist_file.Get(f"WJets_{args.variable}")
h_WJets.SetFillColor(ROOT.kAzure + 1)
h_WJets.SetLineColor(ROOT.kAzure + 1)
h_WJets.SetFillStyle(1001)
legend.AddEntry(h_WJets, "W + Jets", "f")

h_QCD = hist_file.Get(f"QCD_{args.variable}")
h_QCD.SetFillColor(ROOT.kCyan + 1)
h_QCD.SetLineColor(ROOT.kCyan + 1)
h_QCD.SetFillStyle(1001)
legend.AddEntry(h_QCD, "QCD", "f")

h_DYJets = hist_file.Get(f"DYJets_{args.variable}")
h_DYJets.SetFillColor(ROOT.kRed + 1)
h_DYJets.SetLineColor(ROOT.kRed + 1)
h_DYJets.SetFillStyle(1001)
legend.AddEntry(h_DYJets, "DY Jets", "f")

h_VBS_QCD = hist_file.Get(f"VBS_QCD_{args.variable}")
h_VBS_QCD.SetFillColor(ROOT.kMagenta)
h_VBS_QCD.SetLineColor(ROOT.kMagenta)
h_VBS_QCD.SetFillStyle(1001)
legend.AddEntry(h_VBS_QCD, "VBS QCD", "f")

h_VBS_EWK = hist_file.Get(f"VBS_EWK_{args.variable}")
h_VBS_EWK.SetFillColor(ROOT.kGreen + 1)
h_VBS_EWK.SetLineColor(ROOT.kGreen + 1)
h_VBS_EWK.SetFillStyle(1001)
legend.AddEntry(h_VBS_EWK, "VBS EWK", "f")

h_mc.Add(h_Top)
h_mc.Add(h_WJets)
h_mc.Add(h_QCD)
h_mc.Add(h_DYJets)
h_mc.Add(h_VBS_QCD)
h_mc.Add(h_VBS_EWK)

maxY = max(h_data.GetMaximum(), h_mc.GetMaximum())
minY = min(h_data.GetMinimum(), h_mc.GetMinimum())

h_mc.SetMaximum(maxY * args.scale_y_axis)

canvas = ROOT.TCanvas()

if not args.draw_with_ratio:
        
    h_mc.Draw("hist")
    h_data.Draw("x0 e1 same")

    legend.Draw()

    CMS_text(canvas,
             cms_text_location="inside left",
             cms_pos_y_scale=0.9,
             draw_extra_text=True,
             extra_text_location="inside left below",
             extra_text="#scale[1.0]{Preliminary}",
             draw_lumi_text=True,
             lumi_text="#scale[1.0]{35.9 fb^{-1} (13 TeV)}")

if args.draw_with_ratio:

    h_mc_sum = h_mc.GetStack().Last().Clone("mc_sum")

    h_data_total = h_data.Clone("data_total")
    h_data_total.SetTitle(h_mc.GetTitle())

    ratio = ROOT.TRatioPlot(h_data_total, h_mc_sum)

    ratio.SetGraphDrawOpt(args.lower_graph_draw_opt)

    ratio.SetSeparationMargin(0)
    ratio.SetLeftMargin(canvas.GetLeftMargin())
    ratio.SetRightMargin(canvas.GetRightMargin())
    ratio.SetUpTopMargin(0.075)
    ratio.SetLowBottomMargin(0.40)

    ratio.Draw("grid hideup")

    ratio.GetLowYaxis().SetNdivisions(args.lower_graph_ndivisions_y)
    ratio.GetLowerRefYaxis().CenterTitle()
    ratio.GetLowerRefYaxis().SetTitleSize(0.04)
    ratio.GetLowerRefYaxis().SetTitleOffset(1.8)
    ratio.GetLowerRefYaxis().SetLabelSize(0.035)
    ratio.GetLowerRefYaxis().SetTitle(args.lower_graph_title_y)
    ratio.GetLowerRefGraph().SetMinimum(args.lower_graph_min_y)
    ratio.GetLowerRefGraph().SetMaximum(args.lower_graph_max_y)
    ratio.GetLowerRefGraph().SetMarkerStyle(6)

    upper_pad = ratio.GetUpperPad()
    upper_pad.cd()

    h_mc_sum.Reset()
    h_data_total.Reset()
    h_mc.Draw("ah hist")
    h_data.Draw("x0 e1 same")

    legend.Draw()

    CMS_text(upper_pad,
             cms_text_scale=1.2,
             cms_text_location="inside left",
             draw_extra_text=True,
             extra_text_location="inside left right",
             extra_text="#scale[1.2]{Preliminary}",
             extra_text_pos_x_scale=1.0,
             extra_text_pos_y_scale=1.07,
             draw_lumi_text=True,
             lumi_text="#scale[1.1]{35.9 fb^{-1} (13 TeV)}")
    

os.makedirs(f"{args.plots_dir}", exist_ok=True)

canvas.SaveAs(f"{args.plots_dir}/{args.variable}_{args.hist_file.split(".")[0]}.pdf")

if not args.batch_mode:
    canvas.Draw()
    input("Press any key to exit")

#!/usr/bin/env python3

import ROOT
ROOT.gROOT.SetBatch()
import os
import argparse
from pyroot_cms_scripts import CMS_style, CMS_text
ROOT.gErrorIgnoreLevel = ROOT.kError

parser = argparse.ArgumentParser()

parser.add_argument("--rootfile", type=str, default="test.root")
parser.add_argument("--blind", action="store_true")
parser.add_argument("--year", type=str, default="2016")

args = parser.parse_args()

if args.blind:
    blind_data = [("mva_score", -1.0, 1.0)]
else:
    blind_data = []

set_variable_defaults = """
hist_filename = args.rootfile
variable = "lept_pt1"
title_x = "lept_{1} p_{T}"
units = "GeV"
custom_title_y = ""
show_bw = True
scale_y_axis = 1.4
canvas_log_y = False
axis_max_digits = 4
leg_pos = [0.55, 0.65, 0.95, 0.9]
leg_columns = 2

draw_with_ratio = True

ndivisions_x = 510

upper_pad_min_y = "auto"

lower_graph_draw_opt = "p"
lower_graph_max_y = 2.5
lower_graph_min_y = 0.0
lower_graph_ndivisions_y = 404
lower_graph_title_y = "#frac{Data}{MC}"

skip_Top = False
skip_WJets = False
skip_QCD = True
skip_DYJets = True
skip_VBS_QCD = False
skip_VBS_EWK = False

scale_signal = True
signal_scale = 10

skip_data = False

make_cms_text = True

plots_dir = f"{hist_filename.split('/')[-1].split('.')[0]}"
save_all = True
if save_all:
    os.makedirs(f"{plots_dir}", exist_ok=True)
"""

plot_mc_data = """
print("-----------------------")
print("")
print(hist_filename)
print("")
print("-----------------------")


if units != "":
    title_x = f"{title_x} ({units})"

if custom_title_y == "":
    title_y = "Events"
    
# Force CMS_style
# ==============
ROOT.TGaxis().SetMaxDigits(axis_max_digits)
CMS_style.SetLabelSize(0.042, "XYZ")
CMS_style.SetTitleSize(0.055, "XYZ")
CMS_style.cd()
ROOT.gROOT.ForceStyle()

hist_file = ROOT.TFile.Open(hist_filename)

# make stack of mc samples
# overlay data with points
# ========================
legend = ROOT.TLegend(leg_pos[0], leg_pos[1], leg_pos[2], leg_pos[3])
legend.SetFillStyle(0)
legend.SetBorderSize(0)
legend.SetTextFont(42)
legend.SetTextSize(0.03)
legend.SetNColumns(leg_columns)

h_data = hist_file.Get(f"data_obs_{variable}")
h_data.SetMarkerSize(0.8)

if skip_data:
    h_data.Reset()

if h_data.GetEntries() != 0.0:
    legend.AddEntry(h_data, f"Data ({h_data.Integral():.2f})", "pe")

if len(blind_data) != 0:
    for blind_var in blind_data:
        if blind_var[0] in h_data.GetName():
            binA = h_data.FindBin(blind_var[1])
            binB = h_data.FindBin(blind_var[2])
            for i in range(binA, binB + 1):
                h_data.SetBinContent(i, 0.0)

bw = h_data.GetBinWidth(1)

if show_bw:
    title_y = f"{title_y} / {bw:.2f} {units}"

h_mc = ROOT.THStack("h_mc", f";{title_x};{title_y}")

h_Top = hist_file.Get(f"Top_{variable}")
h_Top.SetFillColor(ROOT.TColor.GetColor(155, 152, 204))
h_Top.SetLineColor(ROOT.TColor.GetColor(155, 152, 204))
h_Top.SetFillStyle(1001)

h_WJets = hist_file.Get(f"WJets_{variable}")
h_WJets.SetFillColor(ROOT.TColor.GetColor(222, 90, 106))
h_WJets.SetLineColor(ROOT.TColor.GetColor(222, 90, 106))
h_WJets.SetFillStyle(1001)

if not skip_DYJets:
    h_DYJets = hist_file.Get(f"DYJets_{variable}")
    h_DYJets.SetFillColor(ROOT.TColor.GetColor(200, 90, 106))
    h_DYJets.SetLineColor(ROOT.TColor.GetColor(200, 90, 106))
    h_DYJets.SetFillStyle(1001)
    if h_DYJets.GetEntries() == 0.0:
        skip_DYJets = True

h_VBS_QCD = hist_file.Get(f"VBS_QCD_{variable}")
h_VBS_QCD.SetFillColor(ROOT.TColor.GetColor(248, 206, 104))
h_VBS_QCD.SetLineColor(ROOT.TColor.GetColor(248, 206, 104))
h_VBS_QCD.SetFillStyle(1001)

h_VBS_EWK = hist_file.Get(f"VBS_EWK_{variable}")
h_VBS_EWK.SetLineColor(ROOT.kBlack)
h_VBS_EWK.SetLineWidth(2)
h_VBS_EWK.SetLineStyle(ROOT.kDashed)
h_VBS_EWK.SetFillStyle(0)

if h_VBS_QCD.GetEntries() == 0.0: skip_VBS_QCD = True
if not skip_VBS_QCD:
    legend.AddEntry(h_VBS_QCD, f"VBS QCD ({h_VBS_QCD.Integral():.2f})", "f")
    h_mc.Add(h_VBS_QCD)

if h_Top.GetEntries() == 0.0: skip_Top = True
if not skip_Top:
    legend.AddEntry(h_Top, f"Top ({h_Top.Integral():.2f})", "f")
    h_mc.Add(h_Top)

if  h_WJets.GetEntries() == 0.0: skip_WJets = True
if not skip_WJets:
    legend.AddEntry(h_WJets, f"W + Jets ({h_WJets.Integral():.2f})", "f")
    h_mc.Add(h_WJets)

if not skip_DYJets:
    legend.AddEntry(h_DYJets, f"DY Jets ({h_DYJets.Integral():.2f})", "f")
    h_mc.Add(h_DYJets)

if h_VBS_EWK.GetEntries() == 0.0: skip_VBS_EWK = True
if not skip_VBS_EWK:
    if scale_signal:
        legend.AddEntry(h_VBS_EWK, f"#splitline{{VBS EWK ({h_VBS_EWK.Integral():.2f})}}{{x {signal_scale}}}", "l")
        h_VBS_EWK.Scale(signal_scale)
    else:
        legend.AddEntry(h_VBS_EWK, f"VBS EWK ({h_VBS_EWK.Integral():.2f})", "l")
        
legend.AddEntry(h_mc, f"Tot. MC ({h_mc.GetStack().Last().Integral():.2f})", "")

maxY = max(h_data.GetMaximum(), h_mc.GetMaximum())
minY = min(h_data.GetMinimum(), h_mc.GetMinimum())

h_mc.SetMaximum(maxY * scale_y_axis)

if upper_pad_min_y != "auto":
    h_mc.SetMinimum(upper_pad_min_y)

h_mc_sum = h_mc.GetStack().Last().Clone("mc_sum")

h_mc_sum_copy_for_errors = h_mc_sum.Clone("mc_sum_errors")
h_mc_sum_copy_for_errors.SetFillStyle(3003)
h_mc_sum_copy_for_errors.SetMarkerStyle(0)
h_mc_sum_copy_for_errors.SetFillColor(1)

h_data_total = h_data.Clone("data_total")
h_data_total.SetTitle(h_mc.GetTitle())

canvas = ROOT.TCanvas()

if canvas_log_y:
    canvas.SetLogy()

if not draw_with_ratio:
        
    h_mc.Draw("hist")
    h_data.Draw("x0 e1 same")
    if not skip_VBS_EWK:
        h_VBS_EWK.Draw("hist same")
    h_mc_sum_copy_for_errors.Draw("e2 same")

    legend.Draw()

    if make_cms_text:
        if args.year == "2016":
            lumi_text = "#scale[1.0]{35.9 fb^{-1} (13 TeV)}"
        if args.year == "2017":
            lumi_text = "#scale[1.0]{41.5 fb^{-1} (13 TeV)}"
        if args.year == "2018":
            lumi_text = "#scale[1.0]{59.74 fb^{-1} (13 TeV)}"
        CMS_text(
            canvas,
            cms_text_location="inside left",
            cms_pos_y_scale=0.9,
            draw_extra_text=True,
            extra_text_location="inside left right",
            extra_text="#scale[1.0]{Preliminary}",
            extra_text_pos_y_scale=0.9,
            draw_lumi_text=True,
            lumi_text=lumi_text
        )

if draw_with_ratio:

    ratio = ROOT.TRatioPlot(h_data_total, h_mc_sum)

    ratio.SetGraphDrawOpt(lower_graph_draw_opt)

    ratio.SetSeparationMargin(0)
    ratio.SetLeftMargin(canvas.GetLeftMargin())
    ratio.SetRightMargin(canvas.GetRightMargin())
    ratio.SetUpTopMargin(0.075)
    ratio.SetLowBottomMargin(0.40)

    ratio.Draw("grid hideup")

    ratio.GetLowYaxis().SetNdivisions(lower_graph_ndivisions_y)
    ratio.GetXaxis().SetNdivisions(ndivisions_x)
    if canvas_log_y:
        ratio.GetXaxis().SetRange(2, 2) # brute force

    ratio.GetLowerRefYaxis().CenterTitle()
    ratio.GetLowerRefYaxis().SetTitleSize(0.04)
    ratio.GetLowerRefYaxis().SetTitleOffset(1.8)
    ratio.GetLowerRefYaxis().SetLabelSize(0.035)
    ratio.GetLowerRefYaxis().SetTitle(lower_graph_title_y)
    ratio.GetLowerRefGraph().SetMinimum(lower_graph_min_y)
    ratio.GetLowerRefGraph().SetMaximum(lower_graph_max_y)
    ratio.GetLowerRefGraph().SetMarkerStyle(20)
    ratio.GetLowerRefGraph().SetMarkerSize(0.5)

    upper_pad = ratio.GetUpperPad()
    upper_pad.cd()

    h_mc_sum.Reset()
    h_data_total.Reset()
    h_mc.Draw("ah hist")
    h_mc_sum_copy_for_errors.Draw("e2 same")
    if not skip_VBS_EWK:
        h_data.Draw("x0 e1 same")
    h_VBS_EWK.Draw("hist same")

    legend.Draw()
    
    if make_cms_text:
        if args.year == "2016":
            lumi_text = "#scale[1.0]{35.9 fb^{-1} (13 TeV)}"
        if args.year == "2017":
            lumi_text = "#scale[1.0]{41.5 fb^{-1} (13 TeV)}"
        if args.year == "2018":
            lumi_text = "#scale[1.0]{59.74 fb^{-1} (13 TeV)}"
        CMS_text(
            upper_pad,
            cms_text_scale=1.2,
            cms_text_location="inside left",
            cms_pos_y_scale=0.95,
            draw_extra_text=True,
            extra_text_location="inside left right",
            extra_text="#scale[1.2]{Preliminary}",
            extra_text_pos_x_scale=1.0,
            extra_text_pos_y_scale=0.94,
            draw_lumi_text=True,
            lumi_text=lumi_text
        )
    
canvas.Draw()

if save_all:
    if canvas_log_y:
        extra_tag = "log"
    else:
        extra_tag = ""
    canvas.SaveAs(f"{plots_dir}/{variable}_{extra_tag}.png")
    canvas.SaveAs(f"{plots_dir}/{variable}_{extra_tag}.pdf")
"""

exec(set_variable_defaults)
total_entries = ROOT.TFile.Open(hist_filename)
h_total_entries = total_entries.Get("total_entries")
canvas = ROOT.TCanvas("", "", 800, 500)
h_total_entries.SetStats(0)
h_total_entries.SetBins(7, 0, 1)
h_total_entries.SetTitle(";;")
h_total_entries.GetYaxis().SetLabelSize(0)
h_total_entries.GetYaxis().SetTickSize(0)
h_total_entries.SetLabelSize(0.05)
h_total_entries.SetMarkerSize(2)
h_total_entries.Draw("hist text0")
print("Raw total entries")
canvas.Draw()
canvas.SaveAs(f"{plots_dir}/total_entries.pdf")
canvas.SaveAs(f"{plots_dir}/total_entries.png")

exec(set_variable_defaults)
hist_file = ROOT.TFile.Open(hist_filename)
selection_code = hist_file.Get("_e/selection_code")
print(selection_code.GetTitle(), file=open(f"{plots_dir}/selection_code.txt", "w"))

exec(set_variable_defaults)
variable = "mva_score_var10"
title_x = "MVA Score"
units = ""
scale_signal = True
canvas_log_y = False
exec(plot_mc_data)
scale_y_axis = 10
upper_pad_min_y = 0.1
scale_signal = False
canvas_log_y = True
exec(plot_mc_data)


exec(set_variable_defaults)
variable = "mva_score_var11"
title_x = "MVA Score"
units = ""
scale_signal = True
canvas_log_y = False
exec(plot_mc_data)
scale_y_axis = 10
upper_pad_min_y = 0.1
scale_signal = False
canvas_log_y = True
exec(plot_mc_data)


exec(set_variable_defaults)
variable = "mva_score_var15"
title_x = "MVA Score"
units = ""
scale_signal = True
canvas_log_y = False
exec(plot_mc_data)
scale_y_axis = 10
upper_pad_min_y = 0.1
scale_signal = False
canvas_log_y = True
exec(plot_mc_data)


exec(set_variable_defaults)
variable = "lept1_pt"
title_x = "p^{T}_{lept1}"
units = "GeV"
scale_signal = True
canvas_log_y = False
exec(plot_mc_data)


exec(set_variable_defaults)
variable = "lept1_eta"
title_x = "#eta_{lept1}"
units = ""
scale_signal = True
canvas_log_y = False
exec(plot_mc_data)


exec(set_variable_defaults)
variable = "lept1_phi"
title_x = "#phi_{lept1}"
units = ""
scale_signal = True
canvas_log_y = False
exec(plot_mc_data)


exec(set_variable_defaults)
variable = "pf_met_corr"
title_x = "PF MET"
units = ""
scale_signal = True
canvas_log_y = False
exec(plot_mc_data)


exec(set_variable_defaults)
variable = "pf_met_corr_phi"
title_x = "#phi_{PF MET}"
units = ""
scale_signal = True
canvas_log_y = False
exec(plot_mc_data)

exec(set_variable_defaults)
variable = "fatjet_m"
title_x = "m_{V}"
units = "GeV"
scale_signal = True
canvas_log_y = False
exec(plot_mc_data)


exec(set_variable_defaults)
variable = "fatjet_pt"
title_x = "p^{T}_{V}"
units = "GeV"
ndivisions_x = 505
scale_signal = True
canvas_log_y = False
exec(plot_mc_data)


exec(set_variable_defaults)
variable = "fatjet_eta"
title_x = "#eta_{V}"
units = ""
scale_signal = True
canvas_log_y = False
exec(plot_mc_data)


exec(set_variable_defaults)
variable = "fatjet_phi"
title_x = "#phi_{V}"
units = ""
scale_signal = True
canvas_log_y = False
exec(plot_mc_data)


exec(set_variable_defaults)
variable = "fatjet_n2b1"
title_x = "N^{1}_{2} (V)"
units = ""
scale_signal = True
canvas_log_y = False
exec(plot_mc_data)


exec(set_variable_defaults)
variable = "fatjet_n2b2"
title_x = "N^{2}_{2} (V)"
units = ""
scale_signal = True
canvas_log_y = False
exec(plot_mc_data)


exec(set_variable_defaults)
variable = "fatjet_tau21"
title_x = "#tau_{21} (V)"
units = ""
scale_signal = True
canvas_log_y = False
exec(plot_mc_data)

exec(set_variable_defaults)
variable = "dijet_m"
title_x = "m_{JJ}"
units = ""
scale_signal = True
canvas_log_y = False
exec(plot_mc_data)


exec(set_variable_defaults)
variable = "dijet_pt"
title_x = "p^{T}_{JJ}"
units = ""
scale_signal = True
canvas_log_y = False
exec(plot_mc_data)


exec(set_variable_defaults)
variable = "dijet_eta"
title_x = "#eta_{JJ}"
units = ""
scale_signal = True
canvas_log_y = False
exec(plot_mc_data)


exec(set_variable_defaults)
variable = "dijet_j1_pt"
title_x = "p^{T}_{J1}"
units = ""
scale_signal = True
canvas_log_y = False
exec(plot_mc_data)


exec(set_variable_defaults)
variable = "dijet_j2_pt"
title_x = "p^{T}_{J2}"
units = ""
scale_signal = True
canvas_log_y = False
exec(plot_mc_data)


exec(set_variable_defaults)
variable = "dijet_j1_eta"
title_x = "#eta_{J1}"
units = ""
scale_signal = True
canvas_log_y = False
exec(plot_mc_data)


exec(set_variable_defaults)
variable = "dijet_j2_eta"
title_x = "#eta_{J2}"
units = ""
scale_signal = True
canvas_log_y = False
exec(plot_mc_data)


exec(set_variable_defaults)
variable = "v_pt"
title_x = "p^{T}_{W}"
units = "GeV"
scale_signal = True
canvas_log_y = False
exec(plot_mc_data)


exec(set_variable_defaults)
variable = "v_eta"
title_x = "#eta_{W}"
units = ""
scale_signal = True
canvas_log_y = False
exec(plot_mc_data)


exec(set_variable_defaults)
variable = "v_mt"
title_x = "m^{T}_{W}"
units = "GeV"
scale_signal = True
canvas_log_y = False
exec(plot_mc_data)


exec(set_variable_defaults)
variable = "vbf_j1_pt"
title_x = "p^{T}_{j1}"
units = "GeV"
scale_signal = True
canvas_log_y = False
exec(plot_mc_data)


exec(set_variable_defaults)
variable = "vbf_j2_pt"
title_x = "p^{T}_{j2}"
units = "GeV"
scale_signal = True
canvas_log_y = False
exec(plot_mc_data)


exec(set_variable_defaults)
variable = "vbf_j1_eta"
title_x = "#eta_{j1}"
units = ""
scale_signal = True
canvas_log_y = False
exec(plot_mc_data)


exec(set_variable_defaults)
variable = "vbf_j2_eta"
title_x = "#eta_{j2}"
units = ""
scale_signal = True
canvas_log_y = False
exec(plot_mc_data)


exec(set_variable_defaults)
variable = "vbf_jj_Deta"
title_x = "|#Delta#eta_{jj}|"
units = ""
skip_data = True
scale_signal = True
canvas_log_y = False
exec(plot_mc_data)


exec(set_variable_defaults)
variable = "vbf_j1_phi"
title_x = "#phi_{j1}"
units = ""
scale_signal = True
canvas_log_y = False
exec(plot_mc_data)


exec(set_variable_defaults)
variable = "vbf_j2_phi"
title_x = "#phi_{j2}"
units = ""
scale_signal = True
canvas_log_y = False
exec(plot_mc_data)


exec(set_variable_defaults)
variable = "vbf_jj_m"
title_x = "m_{jj}"
units = "GeV"
scale_signal = True
canvas_log_y = False
exec(plot_mc_data)


exec(set_variable_defaults)
variable = "boson_centrality"
title_x = "Boson Centrality"
units = ""
scale_signal = True
canvas_log_y = False
exec(plot_mc_data)


exec(set_variable_defaults)
variable = "zeppenfeld_w_Deta"
title_x = "Zeppenfeld* W"
units = ""
scale_signal = True
canvas_log_y = False
exec(plot_mc_data)


exec(set_variable_defaults)
variable = "zeppenfeld_v_Deta"
title_x = "Zeppenfeld* V"
units = ""
scale_signal = True
canvas_log_y = False
exec(plot_mc_data)


exec(set_variable_defaults)
variable = "vv_m"
title_x = "m_{WV}"
units = "GeV"
scale_signal = True
canvas_log_y = False
exec(plot_mc_data)


exec(set_variable_defaults)
variable = "vv_m_11bin"
title_x = "m_{WV}"
units = "GeV"
show_bw = False
scale_signal = True
canvas_log_y = False
exec(plot_mc_data)


exec(set_variable_defaults)
variable = "vv_pt"
title_x = "p^{T}_{WV}"
units = "GeV"
scale_signal = True
canvas_log_y = False
exec(plot_mc_data)


exec(set_variable_defaults)
variable = "vv_eta"
title_x = "#eta_{WV}"
units = ""
scale_signal = True
canvas_log_y = False
exec(plot_mc_data)


exec(set_variable_defaults)
variable = "vv_phi"
title_x = "#phi_{WV}"
units = ""
scale_signal = True
canvas_log_y = False
exec(plot_mc_data)

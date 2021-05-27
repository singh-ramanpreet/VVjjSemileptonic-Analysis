#!/usr/bin/env python3

import ROOT
import ctypes
ROOT.gROOT.SetBatch()
ROOT.PyConfig.IgnoreCommandLineOptions = True
import os
import argparse
from pyroot_cms_scripts import CMS_style, CMS_text
ROOT.gErrorIgnoreLevel = ROOT.kError

parser = argparse.ArgumentParser()

parser.add_argument("-f", "--rootfile", type=str, default="test.root")
parser.add_argument("-b", "--blind", action="store_true")
parser.add_argument("-y", "--year", type=str, default="2016")
parser.add_argument("-s", "--sub-dir", dest="sub_dir", type=str, default="/")
parser.add_argument("-m", "--mva-type", dest="mva_type", type=str, default="wjj")
parser.add_argument("-B", "--boson", type=str, default="W")
parser.add_argument("--vars", action="append", default=[])
parser.add_argument("--sys", action="append", default=[])
parser.add_argument("--norm-top", dest="norm_top", type=float, default=0.0)
parser.add_argument("--norm-vjet", dest="norm_vjet", type=float, default=0.0)
parser.add_argument("--wjet-opt", type=int, default=0)
parser.add_argument("--dyjet-opt", type=int, default=0)


args = parser.parse_args()

if args.blind:
    blind_data = [("mva_score", -1.0, 1.0), ("vbf_jj_Deta", 0.0, 10.0),
                  ("nJet30", 0, 8), ("nBtag_loose", 0, 8)]
else:
    blind_data = []

set_variable_defaults = """
hist_filename = args.rootfile
hists_subdirectory = args.sub_dir
variable = ""
title_x = ""
units = ""
custom_title_y = ""
show_bw = True
scale_y_axis = 1.8
canvas_log_y = False
axis_max_digits = 4
leg_pos = [0.42, 0.75, 0.95, 0.9]
leg_columns = 2

draw_with_ratio = True

ndivisions_x = 510

upper_pad_min_y = "auto"

lower_graph_draw_opt = "p"
lower_graph_max_y = 2.0
lower_graph_min_y = 0.0
lower_graph_ndivisions_y = 404
lower_graph_title_y = "#frac{Data}{MC}"

skip_Top = False
skip_WJets = False
skip_DYJets = False
skip_VBS_QCD = False
skip_VBS_EWK = False
skip_data = False

if args.boson == "Z":
    skip_WJets = True

if args.boson == "W":
    skip_DYJets = True

signal_scale_up = 10

make_cms_text = True

plots_dir = f"{hist_filename.split('/')[-1].split('.')[0]}"
os.makedirs(f"{plots_dir}/{hists_subdirectory}", exist_ok=True)
"""

plot_mc_data = """
print("-----------------------")
print("")
print(variable)
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
CMS_style.SetHatchesLineWidth(1)
CMS_style.SetHatchesSpacing(2.5)
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
#legend.SetTextSize(0.04)
legend.SetNColumns(leg_columns)

h_mc_sum = hist_file.Get(f"{hists_subdirectory}/Total_Bkg_{variable}")
post_fit = True
if type(h_mc_sum) == ROOT.TObject:
    post_fit = False

h_data = hist_file.Get(f"{hists_subdirectory}/data_obs_{variable}")
if type(h_data) == ROOT.TObject:
    # no data histogram, get some other to get the binning
    h_data = hist_file.Get(f"{hists_subdirectory}/VBS_EWK_{variable}").Clone(f"data_obs_{variable}")
    skip_data = True

h_data.SetMarkerSize(0.8)

if skip_data:
    h_data.Reset()

if len(blind_data) != 0:
    for blind_var in blind_data:
        if blind_var[0] in h_data.GetName():
            binA = h_data.FindBin(blind_var[1])
            binB = h_data.FindBin(blind_var[2])
            for i in range(binA, binB + 1):
                h_data.SetBinContent(i, 0.0)

if h_data.GetEntries() != 0.0:
    if post_fit:
        legend.AddEntry(h_data, f"Asimov Data ({h_data.Integral():.2f})", "pe")
    else:
        legend.AddEntry(h_data, f"Data ({h_data.Integral():.2f})", "pe")

bw = h_data.GetBinWidth(1)

if show_bw:
    title_y = f"{title_y} / {bw:.2f} {units}"

h_mc = ROOT.THStack("h_mc", f";{title_x};{title_y}")
h_mc_sysUp = ROOT.THStack("h_mc_sysUp", f";{title_x};{title_y}")
h_mc_sysDown = ROOT.THStack("h_mc_sysDown", f";{title_x};{title_y}")

def add_errors(x1, x2):
    return (x1**2 + x2**2)**0.5

if not skip_VBS_QCD:
    h_VBS_QCD = hist_file.Get(f"{hists_subdirectory}/VBS_QCD_{variable}")
    h_VBS_QCD.__getattribute__("SetFillColor")(ROOT.TColor.GetColor(248, 206, 104))
    h_VBS_QCD.__getattribute__("SetLineColor")(ROOT.TColor.GetColor(248, 206, 104))
    h_VBS_QCD.__getattribute__("SetFillStyle")(1001)

    h_VBS_QCD_sysUp = h_VBS_QCD.Clone("VBS_QCD_sysUp")
    h_VBS_QCD_sysDown = h_VBS_QCD.Clone("VBS_QCD_sysDown")

    for i in range(1, h_VBS_QCD.GetNbinsX() + 1):
        sysUp = 0.0
        sysDown = 0.0
        for sys in args.sys:
            htemp_Up = hist_file.Get(f"{hists_subdirectory}_{sys}Up/VBS_QCD_{variable}")
            htemp_Down = hist_file.Get(f"{hists_subdirectory}_{sys}Down/VBS_QCD_{variable}")
            if type(htemp_Up) == ROOT.TObject: continue

            sysUp = add_errors(sysUp, abs(h_VBS_QCD_sysUp.GetBinContent(i) - htemp_Up.GetBinContent(i)))
            sysDown = add_errors(sysDown, abs(h_VBS_QCD_sysDown.GetBinContent(i) - htemp_Down.GetBinContent(i)))
        h_VBS_QCD_sysUp.SetBinContent(i, h_VBS_QCD.GetBinContent(i) + sysUp)
        h_VBS_QCD_sysDown.SetBinContent(i, h_VBS_QCD.GetBinContent(i) - sysDown)

    if h_VBS_QCD.GetEntries() != 0.0:
        error = ctypes.c_double(0.0)
        bin_last = h_VBS_QCD.GetNbinsX()
        integral = h_VBS_QCD.IntegralAndError(0, bin_last, error)
        legend.AddEntry(h_VBS_QCD, f"VBS QCD ({integral:.2f})", "f")
        h_mc.Add(h_VBS_QCD)
        h_mc_sysUp.Add(h_VBS_QCD_sysUp)
        h_mc_sysDown.Add(h_VBS_QCD_sysDown)

if not skip_Top:
    h_Top = hist_file.Get(f"{hists_subdirectory}/Top_{variable}")
    h_Top.__getattribute__("SetFillColor")(ROOT.TColor.GetColor(155, 152, 204))
    h_Top.__getattribute__("SetLineColor")(ROOT.TColor.GetColor(155, 152, 204))
    h_Top.__getattribute__("SetFillStyle")(1001)

    h_Top_sysUp = h_Top.Clone("Top_sysUp")
    h_Top_sysDown = h_Top.Clone("Top_sysDown")
    h_Top_NormUp = h_Top.Clone("Top_NormUp")
    h_Top_NormUp.Scale(float(1 + args.norm_top))
    h_Top_NormDown = h_Top.Clone("Top_NormDown")
    h_Top_NormDown.Scale(float(1 - args.norm_top))

    for i in range(1, h_Top.GetNbinsX() + 1):
        sysUp = 0.0
        sysDown = 0.0
        sysUp = add_errors(sysUp, abs(h_Top.GetBinContent(i) - h_Top_NormUp.GetBinContent(i)))
        sysDown = add_errors(sysDown, abs(h_Top.GetBinContent(i) - h_Top_NormDown.GetBinContent(i)))
        for sys in args.sys:
            htemp_Up = hist_file.Get(f"{hists_subdirectory}_{sys}Up/Top_{variable}")
            htemp_Down = hist_file.Get(f"{hists_subdirectory}_{sys}Down/Top_{variable}")
            if type(htemp_Up) == ROOT.TObject: continue

            sysUp = add_errors(sysUp, abs(h_Top_sysUp.GetBinContent(i) - htemp_Up.GetBinContent(i)))
            sysDown = add_errors(sysDown, abs(h_Top_sysDown.GetBinContent(i) - htemp_Down.GetBinContent(i)))
        h_Top_sysUp.SetBinContent(i, h_Top.GetBinContent(i) + sysUp)
        h_Top_sysDown.SetBinContent(i, h_Top.GetBinContent(i) - sysDown)

    if h_Top.GetEntries() != 0.0:
        error = ctypes.c_double(0.0)
        bin_last = h_Top.GetNbinsX()
        integral = h_Top.IntegralAndError(0, bin_last, error)
        #legend.AddEntry(h_Top, f"Top ({integral:.2f}, {error.value:.2f})", "f")
        legend.AddEntry(h_Top, f"Top ({integral:.2f})", "f")
        h_mc.Add(h_Top)
        h_mc_sysUp.Add(h_Top_sysUp)
        h_mc_sysDown.Add(h_Top_sysDown)

if not skip_WJets:
    WJets_option = args.wjet_opt

    if WJets_option == 0:

        h_WJets = hist_file.Get(f"{hists_subdirectory}/WJets_HT_{variable}")
        h_WJets.SetFillColor(ROOT.TColor.GetColor(222, 90, 106))
        h_WJets.SetLineColor(ROOT.TColor.GetColor(222, 90, 106))
        h_WJets.SetFillStyle(1001)

        h_WJets_sysUp = h_WJets.Clone("WJets_sysUp")
        h_WJets_sysDown = h_WJets.Clone("WJets_sysDown")
        h_WJets_NormUp = h_WJets.Clone("WJets_NormUp")
        h_WJets_NormUp.Scale(float(1 + args.norm_vjet))
        h_WJets_NormDown = h_WJets.Clone("WJets_NormDown")
        h_WJets_NormDown.Scale(float(1 - args.norm_vjet))

        for i in range(1, h_WJets.GetNbinsX() + 1):
            sysUp = 0.0
            sysDown = 0.0
            sysUp = add_errors(sysUp, abs(h_WJets.GetBinContent(i) - h_WJets_NormUp.GetBinContent(i)))
            sysDown = add_errors(sysDown, abs(h_WJets.GetBinContent(i) - h_WJets_NormDown.GetBinContent(i)))
            for sys in args.sys:
                htemp_Up = hist_file.Get(f"{hists_subdirectory}_{sys}Up/WJets_HT_{variable}")
                htemp_Down = hist_file.Get(f"{hists_subdirectory}_{sys}Down/WJets_HT_{variable}")
                if type(htemp_Up) == ROOT.TObject: continue

                sysUp = add_errors(sysUp, abs(h_WJets_sysUp.GetBinContent(i) - htemp_Up.GetBinContent(i)))
                sysDown = add_errors(sysDown, abs(h_WJets_sysDown.GetBinContent(i) - htemp_Down.GetBinContent(i)))
            h_WJets_sysUp.SetBinContent(i, h_WJets.GetBinContent(i) + sysUp)
            h_WJets_sysDown.SetBinContent(i, h_WJets.GetBinContent(i) - sysDown)

        if h_WJets.GetEntries() != 0.0:
            error = ctypes.c_double(0.0)
            bin_last = h_WJets.GetNbinsX()
            integral = h_WJets.IntegralAndError(0, bin_last, error)
            #legend.AddEntry(h_WJets, f"W + Jets ({integral:.2f}, {error.value:.2f})", "f")
            legend.AddEntry(h_WJets, f"W + Jets ({integral:.2f})", "f")
            h_mc.Add(h_WJets)
            h_mc_sysUp.Add(h_WJets_sysUp)
            h_mc_sysDown.Add(h_WJets_sysDown)

    if WJets_option == 1:

        h_WJets_b1 = hist_file.Get(f"{hists_subdirectory}/WJets_HT_b1_{variable}")
        h_WJets_b1.SetFillColor(ROOT.TColor.GetColor(222, 90, 106))
        h_WJets_b1.SetLineColor(ROOT.TColor.GetColor(222, 90, 106))
        h_WJets_b1.SetFillStyle(1001)

        h_WJets_b1_sysUp = h_WJets_b1.Clone("WJets_b1_sysUp")
        h_WJets_b1_sysDown = h_WJets_b1.Clone("WJets_b1_sysDown")
        h_WJets_b1_NormUp = h_WJets_b1.Clone("WJets_b1_NormUp")
        h_WJets_b1_NormUp.Scale(float(1 + args.norm_vjet))
        h_WJets_b1_NormDown = h_WJets_b1.Clone("WJets_b1_NormDown")
        h_WJets_b1_NormDown.Scale(float(1 - args.norm_vjet))

        for i in range(1, h_WJets_b1.GetNbinsX() + 1):
            sysUp = 0.0
            sysDown = 0.0
            sysUp = add_errors(sysUp, abs(h_WJets_b1.GetBinContent(i) - h_WJets_b1_NormUp.GetBinContent(i)))
            sysDown = add_errors(sysDown, abs(h_WJets_b1.GetBinContent(i) - h_WJets_b1_NormDown.GetBinContent(i)))
            for sys in args.sys:
                htemp_Up = hist_file.Get(f"{hists_subdirectory}_{sys}Up/WJets_HT_b1_{variable}")
                htemp_Down = hist_file.Get(f"{hists_subdirectory}_{sys}Down/WJets_HT_b1_{variable}")
                if type(htemp_Up) == ROOT.TObject: continue

                sysUp = add_errors(sysUp, abs(h_WJets_b1_sysUp.GetBinContent(i) - htemp_Up.GetBinContent(i)))
                sysDown = add_errors(sysDown, abs(h_WJets_b1_sysDown.GetBinContent(i) - htemp_Down.GetBinContent(i)))
            h_WJets_b1_sysUp.SetBinContent(i, h_WJets_b1.GetBinContent(i) + sysUp)
            h_WJets_b1_sysDown.SetBinContent(i, h_WJets_b1.GetBinContent(i) - sysDown)

        if h_WJets_b1.GetEntries() != 0.0:
            error = ctypes.c_double(0.0)
            bin_last = h_WJets_b1.GetNbinsX()
            integral = h_WJets_b1.IntegralAndError(0, bin_last, error)
            #legend.AddEntry(h_WJets_b1, f"W + Jets b1 ({integral:.2f}, {error.value:.2f})", "f")
            legend.AddEntry(h_WJets_b1, f"W + Jets b1 ({integral:.2f})", "f")
            h_mc.Add(h_WJets_b1)
            h_mc_sysUp.Add(h_WJets_b1_sysUp)
            h_mc_sysDown.Add(h_WJets_b1_sysDown)


        h_WJets_b2 = hist_file.Get(f"{hists_subdirectory}/WJets_HT_b2_{variable}")
        h_WJets_b2.SetFillColor(ROOT.TColor.GetColor(222 - 40, 90 - 20, 106 - 20))
        h_WJets_b2.SetLineColor(ROOT.TColor.GetColor(222 - 40, 90 - 20, 106 - 20))
        h_WJets_b2.SetFillStyle(1001)

        h_WJets_b2_sysUp = h_WJets_b2.Clone("WJets_b2_sysUp")
        h_WJets_b2_sysDown = h_WJets_b2.Clone("WJets_b2_sysDown")
        h_WJets_b2_NormUp = h_WJets_b2.Clone("WJets_b2_NormUp")
        h_WJets_b2_NormUp.Scale(float(1 + args.norm_vjet))
        h_WJets_b2_NormDown = h_WJets_b2.Clone("WJets_b2_NormDown")
        h_WJets_b2_NormDown.Scale(float(1 - args.norm_vjet))

        for i in range(1, h_WJets_b2.GetNbinsX() + 1):
            sysUp = 0.0
            sysDown = 0.0
            sysUp = add_errors(sysUp, abs(h_WJets_b2.GetBinContent(i) - h_WJets_b2_NormUp.GetBinContent(i)))
            sysDown = add_errors(sysDown, abs(h_WJets_b2.GetBinContent(i) - h_WJets_b2_NormDown.GetBinContent(i)))
            for sys in args.sys:
                htemp_Up = hist_file.Get(f"{hists_subdirectory}_{sys}Up/WJets_HT_b2_{variable}")
                htemp_Down = hist_file.Get(f"{hists_subdirectory}_{sys}Down/WJets_HT_b2_{variable}")
                if type(htemp_Up) == ROOT.TObject: continue

                sysUp = add_errors(sysUp, abs(h_WJets_b2_sysUp.GetBinContent(i) - htemp_Up.GetBinContent(i)))
                sysDown = add_errors(sysDown, abs(h_WJets_b2_sysDown.GetBinContent(i) - htemp_Down.GetBinContent(i)))
            h_WJets_b2_sysUp.SetBinContent(i, h_WJets_b2.GetBinContent(i) + sysUp)
            h_WJets_b2_sysDown.SetBinContent(i, h_WJets_b2.GetBinContent(i) - sysDown)

        if h_WJets_b2.GetEntries() != 0.0:
            error = ctypes.c_double(0.0)
            bin_last = h_WJets_b2.GetNbinsX()
            integral = h_WJets_b2.IntegralAndError(0, bin_last, error)
            #legend.AddEntry(h_WJets_b2, f"W + Jets b2 ({integral:.2f}, {error.value:.2f})", "f")
            legend.AddEntry(h_WJets_b2, f"W + Jets b2 ({integral:.2f})", "f")
            h_mc.Add(h_WJets_b2)
            h_mc_sysUp.Add(h_WJets_b2_sysUp)
            h_mc_sysDown.Add(h_WJets_b2_sysDown)

    if WJets_option == 2:

        h_WJets_r1 = hist_file.Get(f"{hists_subdirectory}/WJets_HT_r1_{variable}")
        h_WJets_r1.SetFillColor(ROOT.TColor.GetColor(222, 90, 106))
        h_WJets_r1.SetLineColor(ROOT.TColor.GetColor(222, 90, 106))
        h_WJets_r1.SetFillStyle(1001)

        h_WJets_r1_sysUp = h_WJets_r1.Clone("WJets_r1_sysUp")
        h_WJets_r1_sysDown = h_WJets_r1.Clone("WJets_r1_sysDown")
        h_WJets_r1_NormUp = h_WJets_r1.Clone("WJets_r1_NormUp")
        h_WJets_r1_NormUp.Scale(float(1 + args.norm_vjet))
        h_WJets_r1_NormDown = h_WJets_r1.Clone("WJets_r1_NormDown")
        h_WJets_r1_NormDown.Scale(float(1 - args.norm_vjet))

        for i in range(1, h_WJets_r1.GetNbinsX() + 1):
            sysUp = 0.0
            sysDown = 0.0
            sysUp = add_errors(sysUp, abs(h_WJets_r1.GetBinContent(i) - h_WJets_r1_NormUp.GetBinContent(i)))
            sysDown = add_errors(sysDown, abs(h_WJets_r1.GetBinContent(i) - h_WJets_r1_NormDown.GetBinContent(i)))
            for sys in args.sys:
                htemp_Up = hist_file.Get(f"{hists_subdirectory}_{sys}Up/WJets_HT_r1_{variable}")
                htemp_Down = hist_file.Get(f"{hists_subdirectory}_{sys}Down/WJets_HT_r1_{variable}")
                if type(htemp_Up) == ROOT.TObject: continue

                sysUp = add_errors(sysUp, abs(h_WJets_r1_sysUp.GetBinContent(i) - htemp_Up.GetBinContent(i)))
                sysDown = add_errors(sysDown, abs(h_WJets_r1_sysDown.GetBinContent(i) - htemp_Down.GetBinContent(i)))
            h_WJets_r1_sysUp.SetBinContent(i, h_WJets_r1.GetBinContent(i) + sysUp)
            h_WJets_r1_sysDown.SetBinContent(i, h_WJets_r1.GetBinContent(i) - sysDown)

        if h_WJets_r1.GetEntries() != 0.0:
            error = ctypes.c_double(0.0)
            bin_last = h_WJets_r1.GetNbinsX()
            integral = h_WJets_r1.IntegralAndError(0, bin_last, error)
            #legend.AddEntry(h_WJets_r1, f"W + Jets r1 ({integral:.2f}, {error.value:.2f})", "f")
            legend.AddEntry(h_WJets_r1, f"W + Jets r1 ({integral:.2f})", "f")
            h_mc.Add(h_WJets_r1)
            h_mc_sysUp.Add(h_WJets_r1_sysUp)
            h_mc_sysDown.Add(h_WJets_r1_sysDown)

        h_WJets_r2 = hist_file.Get(f"{hists_subdirectory}/WJets_HT_r2_{variable}")
        h_WJets_r2.SetFillColor(ROOT.TColor.GetColor(222 - 40, 90 - 20, 106 - 20))
        h_WJets_r2.SetLineColor(ROOT.TColor.GetColor(222 - 40, 90 - 20, 106 - 20))
        h_WJets_r2.SetFillStyle(1001)

        h_WJets_r2_sysUp = h_WJets_r2.Clone("WJets_r2_sysUp")
        h_WJets_r2_sysDown = h_WJets_r2.Clone("WJets_r2_sysDown")
        h_WJets_r2_NormUp = h_WJets_r2.Clone("WJets_r2_NormUp")
        h_WJets_r2_NormUp.Scale(float(1 + args.norm_vjet))
        h_WJets_r2_NormDown = h_WJets_r2.Clone("WJets_r2_NormDown")
        h_WJets_r2_NormDown.Scale(float(1 - args.norm_vjet))

        for i in range(1, h_WJets_r2.GetNbinsX() + 1):
            sysUp = 0.0
            sysDown = 0.0
            sysUp = add_errors(sysUp, abs(h_WJets_r2.GetBinContent(i) - h_WJets_r2_NormUp.GetBinContent(i)))
            sysDown = add_errors(sysDown, abs(h_WJets_r2.GetBinContent(i) - h_WJets_r2_NormDown.GetBinContent(i)))
            for sys in args.sys:
                htemp_Up = hist_file.Get(f"{hists_subdirectory}_{sys}Up/WJets_HT_r2_{variable}")
                htemp_Down = hist_file.Get(f"{hists_subdirectory}_{sys}Down/WJets_HT_r2_{variable}")
                if type(htemp_Up) == ROOT.TObject: continue

                sysUp = add_errors(sysUp, abs(h_WJets_r2_sysUp.GetBinContent(i) - htemp_Up.GetBinContent(i)))
                sysDown = add_errors(sysDown, abs(h_WJets_r2_sysDown.GetBinContent(i) - htemp_Down.GetBinContent(i)))
            h_WJets_r2_sysUp.SetBinContent(i, h_WJets_r2.GetBinContent(i) + sysUp)
            h_WJets_r2_sysDown.SetBinContent(i, h_WJets_r2.GetBinContent(i) - sysDown)

        if h_WJets_r2.GetEntries() != 0.0:
            error = ctypes.c_double(0.0)
            bin_last = h_WJets_r2.GetNbinsX()
            integral = h_WJets_r2.IntegralAndError(0, bin_last, error)
            #legend.AddEntry(h_WJets_r2, f"W + Jets r2 ({integral:.2f}, {error.value:.2f})", "f")
            legend.AddEntry(h_WJets_r2, f"W + Jets r2 ({integral:.2f})", "f")
            h_mc.Add(h_WJets_r2)
            h_mc_sysUp.Add(h_WJets_r2_sysUp)
            h_mc_sysDown.Add(h_WJets_r2_sysDown)

        h_WJets_r3 = hist_file.Get(f"{hists_subdirectory}/WJets_HT_r3_{variable}")
        h_WJets_r3.SetFillColor(ROOT.TColor.GetColor(222 - 60, 90 - 40, 106 - 40))
        h_WJets_r3.SetLineColor(ROOT.TColor.GetColor(222 - 60, 90 - 40, 106 - 40))
        h_WJets_r3.SetFillStyle(1001)

        h_WJets_r3_sysUp = h_WJets_r3.Clone("WJets_r3_sysUp")
        h_WJets_r3_sysDown = h_WJets_r3.Clone("WJets_r3_sysDown")
        h_WJets_r3_NormUp = h_WJets_r3.Clone("WJets_r3_NormUp")
        h_WJets_r3_NormUp.Scale(float(1 + args.norm_vjet))
        h_WJets_r3_NormDown = h_WJets_r3.Clone("WJets_r3_NormDown")
        h_WJets_r3_NormDown.Scale(float(1 - args.norm_vjet))

        for i in range(1, h_WJets_r3.GetNbinsX() + 1):
            sysUp = 0.0
            sysDown = 0.0
            sysUp = add_errors(sysUp, abs(h_WJets_r3.GetBinContent(i) - h_WJets_r3_NormUp.GetBinContent(i)))
            sysDown = add_errors(sysDown, abs(h_WJets_r3.GetBinContent(i) - h_WJets_r3_NormDown.GetBinContent(i)))
            for sys in args.sys:
                htemp_Up = hist_file.Get(f"{hists_subdirectory}_{sys}Up/WJets_HT_r3_{variable}")
                htemp_Down = hist_file.Get(f"{hists_subdirectory}_{sys}Down/WJets_HT_r3_{variable}")
                if type(htemp_Up) == ROOT.TObject: continue

                sysUp = add_errors(sysUp, abs(h_WJets_r3_sysUp.GetBinContent(i) - htemp_Up.GetBinContent(i)))
                sysDown = add_errors(sysDown, abs(h_WJets_r3_sysDown.GetBinContent(i) - htemp_Down.GetBinContent(i)))
            h_WJets_r3_sysUp.SetBinContent(i, h_WJets_r3.GetBinContent(i) + sysUp)
            h_WJets_r3_sysDown.SetBinContent(i, h_WJets_r3.GetBinContent(i) - sysDown)

        if h_WJets_r3.GetEntries() != 0.0:
            error = ctypes.c_double(0.0)
            bin_last = h_WJets_r3.GetNbinsX()
            integral = h_WJets_r3.IntegralAndError(0, bin_last, error)
            #legend.AddEntry(h_WJets_r3, f"W + Jets r3 ({integral:.2f}, {error.value:.2f})", "f")
            legend.AddEntry(h_WJets_r3, f"W + Jets r3 ({integral:.2f})", "f")
            h_mc.Add(h_WJets_r3)
            h_mc_sysUp.Add(h_WJets_r3_sysUp)
            h_mc_sysDown.Add(h_WJets_r3_sysDown)

        h_WJets_r4 = hist_file.Get(f"{hists_subdirectory}/WJets_HT_r4_{variable}")
        h_WJets_r4.SetFillColor(ROOT.TColor.GetColor(238, 135, 0))
        h_WJets_r4.SetLineColor(ROOT.TColor.GetColor(238, 135, 0))
        h_WJets_r4.SetFillStyle(1001)

        h_WJets_r4_sysUp = h_WJets_r4.Clone("WJets_r4_sysUp")
        h_WJets_r4_sysDown = h_WJets_r4.Clone("WJets_r4_sysDown")
        h_WJets_r4_NormUp = h_WJets_r4.Clone("WJets_r4_NormUp")
        h_WJets_r4_NormUp.Scale(float(1 + args.norm_vjet))
        h_WJets_r4_NormDown = h_WJets_r4.Clone("WJets_r4_NormDown")
        h_WJets_r4_NormDown.Scale(float(1 - args.norm_vjet))

        for i in range(1, h_WJets_r4.GetNbinsX() + 1):
            sysUp = 0.0
            sysDown = 0.0
            sysUp = add_errors(sysUp, abs(h_WJets_r4.GetBinContent(i) - h_WJets_r4_NormUp.GetBinContent(i)))
            sysDown = add_errors(sysDown, abs(h_WJets_r4.GetBinContent(i) - h_WJets_r4_NormDown.GetBinContent(i)))
            for sys in args.sys:
                htemp_Up = hist_file.Get(f"{hists_subdirectory}_{sys}Up/WJets_HT_r4_{variable}")
                htemp_Down = hist_file.Get(f"{hists_subdirectory}_{sys}Down/WJets_HT_r4_{variable}")
                if type(htemp_Up) == ROOT.TObject: continue

                sysUp = add_errors(sysUp, abs(h_WJets_r4_sysUp.GetBinContent(i) - htemp_Up.GetBinContent(i)))
                sysDown = add_errors(sysDown, abs(h_WJets_r4_sysDown.GetBinContent(i) - htemp_Down.GetBinContent(i)))
            h_WJets_r4_sysUp.SetBinContent(i, h_WJets_r4.GetBinContent(i) + sysUp)
            h_WJets_r4_sysDown.SetBinContent(i, h_WJets_r4.GetBinContent(i) - sysDown)

        if h_WJets_r4.GetEntries() != 0.0:
            error = ctypes.c_double(0.0)
            bin_last = h_WJets_r4.GetNbinsX()
            integral = h_WJets_r4.IntegralAndError(0, bin_last, error)
            #legend.AddEntry(h_WJets_r4, f"W + Jets r4 ({integral:.2f}, {error.value:.2f})", "f")
            legend.AddEntry(h_WJets_r4, f"W + Jets r4 ({integral:.2f})", "f")
            h_mc.Add(h_WJets_r4)
            h_mc_sysUp.Add(h_WJets_r4_sysUp)
            h_mc_sysDown.Add(h_WJets_r4_sysDown)

        h_WJets_r5 = hist_file.Get(f"{hists_subdirectory}/WJets_HT_r5_{variable}")
        h_WJets_r5.SetFillColor(ROOT.TColor.GetColor(212, 120, 0))
        h_WJets_r5.SetLineColor(ROOT.TColor.GetColor(212, 120, 0))
        h_WJets_r5.SetFillStyle(1001)

        h_WJets_r5_sysUp = h_WJets_r5.Clone("WJets_r5_sysUp")
        h_WJets_r5_sysDown = h_WJets_r5.Clone("WJets_r5_sysDown")
        h_WJets_r5_NormUp = h_WJets_r5.Clone("WJets_r5_NormUp")
        h_WJets_r5_NormUp.Scale(float(1 + args.norm_vjet))
        h_WJets_r5_NormDown = h_WJets_r5.Clone("WJets_r5_NormDown")
        h_WJets_r5_NormDown.Scale(float(1 - args.norm_vjet))

        for i in range(1, h_WJets_r5.GetNbinsX() + 1):
            sysUp = 0.0
            sysDown = 0.0
            sysUp = add_errors(sysUp, abs(h_WJets_r5.GetBinContent(i) - h_WJets_r5_NormUp.GetBinContent(i)))
            sysDown = add_errors(sysDown, abs(h_WJets_r5.GetBinContent(i) - h_WJets_r5_NormDown.GetBinContent(i)))
            for sys in args.sys:
                htemp_Up = hist_file.Get(f"{hists_subdirectory}_{sys}Up/WJets_HT_r5_{variable}")
                htemp_Down = hist_file.Get(f"{hists_subdirectory}_{sys}Down/WJets_HT_r5_{variable}")
                if type(htemp_Up) == ROOT.TObject: continue

                sysUp = add_errors(sysUp, abs(h_WJets_r5_sysUp.GetBinContent(i) - htemp_Up.GetBinContent(i)))
                sysDown = add_errors(sysDown, abs(h_WJets_r5_sysDown.GetBinContent(i) - htemp_Down.GetBinContent(i)))
            h_WJets_r5_sysUp.SetBinContent(i, h_WJets_r5.GetBinContent(i) + sysUp)
            h_WJets_r5_sysDown.SetBinContent(i, h_WJets_r5.GetBinContent(i) - sysDown)

        if h_WJets_r5.GetEntries() != 0.0:
            error = ctypes.c_double(0.0)
            bin_last = h_WJets_r5.GetNbinsX()
            integral = h_WJets_r5.IntegralAndError(0, bin_last, error)
            #legend.AddEntry(h_WJets_r5, f"W + Jets r5 ({integral:.2f}, {error.value:.2f})", "f")
            legend.AddEntry(h_WJets_r5, f"W + Jets r5 ({integral:.2f})", "f")
            h_mc.Add(h_WJets_r5)
            h_mc_sysUp.Add(h_WJets_r5_sysUp)
            h_mc_sysDown.Add(h_WJets_r5_sysDown)

if not skip_DYJets:

    if args.dyjet_opt == 0:
        dyjets_tag = "DYJets_LO"

    if args.dyjet_opt == 1:
        dyjets_tag = "DYJets_HT"

    h_DYJets = hist_file.Get(f"{hists_subdirectory}/{dyjets_tag}_{variable}")
    h_DYJets.SetFillColor(ROOT.TColor.GetColor(200, 90, 106))
    h_DYJets.SetLineColor(ROOT.TColor.GetColor(200, 90, 106))
    h_DYJets.SetFillStyle(1001)

    h_DYJets_sysUp = h_DYJets.Clone("DYJets_sysUp")
    h_DYJets_sysDown = h_DYJets.Clone("DYJets_sysDown")
    h_DYJets_NormUp = h_DYJets.Clone("DYJets_NormUp")
    h_DYJets_NormUp.Scale(float(1 + args.norm_vjet))
    h_DYJets_NormDown = h_DYJets.Clone("DYJets_NormDown")
    h_DYJets_NormDown.Scale(float(1 - args.norm_vjet))

    for i in range(1, h_DYJets.GetNbinsX() + 1):
        sysUp = 0.0
        sysDown = 0.0
        sysUp = add_errors(sysUp, abs(h_DYJets.GetBinContent(i) - h_DYJets_NormUp.GetBinContent(i)))
        sysDown = add_errors(sysDown, abs(h_DYJets.GetBinContent(i) - h_DYJets_NormDown.GetBinContent(i)))
        for sys in args.sys:
            htemp_Up = hist_file.Get(f"{hists_subdirectory}_{sys}Up/{dyjets_tag}_{variable}")
            htemp_Down = hist_file.Get(f"{hists_subdirectory}_{sys}Down/{dyjets_tag}_{variable}")
            if type(htemp_Up) == ROOT.TObject: continue

            sysUp = add_errors(sysUp, abs(h_DYJets_sysUp.GetBinContent(i) - htemp_Up.GetBinContent(i)))
            sysDown = add_errors(sysDown, abs(h_DYJets_sysDown.GetBinContent(i) - htemp_Down.GetBinContent(i)))
        h_DYJets_sysUp.SetBinContent(i, h_DYJets.GetBinContent(i) + sysUp)
        h_DYJets_sysDown.SetBinContent(i, h_DYJets.GetBinContent(i) - sysDown)

    if h_DYJets.GetEntries() != 0.0:
        error = ctypes.c_double(0.0)
        bin_last = h_DYJets.GetNbinsX()
        integral = h_DYJets.IntegralAndError(0, bin_last, error)
        #legend.AddEntry(h_DYJets, f"DY Jets ({integral:.2f}, {error.value:.2f})", "f")
        legend.AddEntry(h_DYJets, f"DY Jets ({integral:.2f})", "f")
        h_mc.Add(h_DYJets)
        h_mc_sysUp.Add(h_DYJets_sysUp)
        h_mc_sysDown.Add(h_DYJets_sysDown)

if not skip_VBS_EWK:
    h_VBS_EWK = hist_file.Get(f"{hists_subdirectory}/VBS_EWK_{variable}")
    h_VBS_EWK.SetLineColor(ROOT.kBlack)
    h_VBS_EWK.SetLineWidth(2)
    h_VBS_EWK.SetLineStyle(ROOT.kDashed)
    h_VBS_EWK.SetFillStyle(0)

    error = ctypes.c_double(0.0)
    bin_last = h_VBS_EWK.GetNbinsX()
    integral = h_VBS_EWK.IntegralAndError(0, bin_last, error)
    if signal_scale_up != 1:
        legend.AddEntry(h_VBS_EWK, f"VBS EWK x{signal_scale_up} ({integral:.2f})", "l")
        h_VBS_EWK.Scale(signal_scale_up)
    else:
        legend.AddEntry(h_VBS_EWK, f"VBS EWK ({integral:.2f})", "l")
        
legend.AddEntry(ROOT.nullptr, f"Total MC ({h_mc.GetStack().Last().Integral():.2f})", "f")

maxY = max(h_data.GetMaximum(), h_mc.GetMaximum())
minY = min(h_data.GetMinimum(), h_mc.GetMinimum())

h_mc.SetMaximum(maxY * scale_y_axis)

if upper_pad_min_y != "auto":
    h_mc.SetMinimum(upper_pad_min_y)

if not post_fit:
    h_mc_sum = h_mc.GetStack().Last().Clone("mc_sum")
    h_mc_sumUp = h_mc_sysUp.GetStack().Last().Clone("mc_sumUp")
    h_mc_sumDown = h_mc_sysUp.GetStack().Last().Clone("mc_sumDown")

g_mc_errors = ROOT.TGraphAsymmErrors(h_mc_sum.Clone("mc_sum_errors"))
g_mc_errors.SetFillStyle(3145)
g_mc_errors.SetMarkerStyle(0)
g_mc_errors.SetFillColor(1)
g_mc_errors.SetLineColor(1)
if post_fit:
    legend.AddEntry(g_mc_errors, "PostFit Unc.", "f")
else:
    legend.AddEntry(g_mc_errors, "Stat + Sys Unc.", "f")

g_mc_errors_ratio = g_mc_errors.Clone("mc_errors_ratio")
g_mc_errors_ratio.SetFillStyle(1001)
g_mc_errors_ratio.SetMarkerStyle(0)
g_mc_errors_ratio.SetFillColor(ROOT.kGray)

for ibin in range(h_mc_sum.GetNbinsX() + 1):
    #print(ibin + 1, h_mc_sum.GetBinError(ibin + 1), g_mc_errors.GetErrorYhigh(ibin), g_mc_errors.GetErrorYlow(ibin))
    if post_fit:
        d_ey_Up = 0.0
        d_ey_Down = 0.0
    else:
        print(ibin, h_mc_sumUp.GetBinContent(ibin + 1))
        d_ey_Up = abs(h_mc_sumUp.GetBinContent(ibin + 1) - h_mc_sum.GetBinContent(ibin + 1))
        d_ey_Down = abs(h_mc_sumDown.GetBinContent(ibin + 1) - h_mc_sum.GetBinContent(ibin + 1))
    #print(d_ey_Up, d_ey_Down)

    ey_Up = add_errors(g_mc_errors.GetErrorYhigh(ibin), d_ey_Up)
    g_mc_errors.SetPointEYhigh(ibin, ey_Up)

    ey_Down = add_errors(g_mc_errors.GetErrorYlow(ibin), d_ey_Down)
    g_mc_errors.SetPointEYlow(ibin, ey_Down)
    #print(ibin + 1, g_mc_errors.GetErrorYhigh(ibin), g_mc_errors.GetErrorYlow(ibin))

    g_mc_errors_ratio.SetPointY(ibin, 1.0)
    if g_mc_errors.GetPointY(ibin) != 0.0:
        g_mc_errors_ratio.SetPointEYhigh(ibin, ey_Up/g_mc_errors.GetPointY(ibin))
        g_mc_errors_ratio.SetPointEYlow(ibin, ey_Down/g_mc_errors.GetPointY(ibin))
    else:
        g_mc_errors_ratio.SetPointEYhigh(ibin, 0.0)
        g_mc_errors_ratio.SetPointEYlow(ibin, 0.0)

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
    g_mc_errors.Draw("2")

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
            extra_text_pos_y_scale=0.95,
            draw_lumi_text=True,
            lumi_text=lumi_text
        )

if draw_with_ratio:

    if h_data_total.Integral() == 0.0:
        # this for blinded plots
        ratio = ROOT.TRatioPlot(h_mc_sum, h_mc_sum)
        lower_graph_title_y = ""
    else:
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

    gridlines = ROOT.std.vector("double")()
    gridlines.push_back(0.5)
    gridlines.push_back(1.0)
    gridlines.push_back(1.5)
    ratio.SetGridlines(gridlines)
    ratio.GetLowerRefYaxis().CenterTitle()
    ratio.GetLowerRefYaxis().SetTitleSize(0.04)
    ratio.GetLowerRefYaxis().SetTitleOffset(1.8)
    ratio.GetLowerRefYaxis().SetLabelSize(0.035)
    ratio.GetLowerRefYaxis().SetTitle(lower_graph_title_y)
    ratio.GetLowerRefGraph().SetMinimum(lower_graph_min_y)
    ratio.GetLowerRefGraph().SetMaximum(lower_graph_max_y)
    ratio.GetLowerRefGraph().SetMarkerStyle(20)
    ratio.GetLowerRefGraph().SetMarkerSize(0.8)

    lower_pad = ratio.GetLowerPad()
    lower_pad.cd()
    g_mc_errors_ratio.Draw("2")
    # draw again, hack
    ratio.GetLowerRefGraph().Draw(f"same {lower_graph_draw_opt}")

    if h_data_total.Integral() == 0.0:
        ratio.GetLowerRefGraph().SetMarkerSize(0.0)
        for i in range(ratio.GetLowerRefGraph().GetN()):
            ratio.GetLowerRefGraph().SetPointError(i, 0, 0, 0, 0)

    upper_pad = ratio.GetUpperPad()
    upper_pad.cd()

    h_mc_sum.Reset()
    h_data_total.Reset()
    h_mc.Draw("ah hist")
    g_mc_errors.Draw("2")
    if not skip_VBS_EWK:
        h_data.Draw("x0 e1 same")
    h_VBS_EWK.Draw("hist same")

    legend.SetY1(legend.GetY2() - 0.05 * legend.GetNRows())
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
            extra_text_pos_y_scale=1.0,
            draw_lumi_text=True,
            lumi_text=lumi_text
        )
    
canvas.Draw()
extra_tag = ""

if canvas_log_y:
    extra_tag += "_log"
else:
    extra_tag += ""

plot_filename = f"{plots_dir}/{hists_subdirectory}/{variable}{extra_tag}"
canvas.SaveAs(f"{plot_filename}.pdf")
os.popen(f"convert -density 150 -antialias {plot_filename}.pdf -trim {plot_filename}.png 2> /dev/null")
"""

#exec(set_variable_defaults)
#total_entries = ROOT.TFile.Open(hist_filename)
#h_total_entries = total_entries.Get("total_entries")
#canvas = ROOT.TCanvas("", "", 800, 500)
#h_total_entries.SetStats(0)
#h_total_entries.SetBins(7, 0, 1)
#h_total_entries.SetTitle(";;")
#h_total_entries.GetYaxis().SetLabelSize(0)
#h_total_entries.GetYaxis().SetTickSize(0)
#h_total_entries.SetLabelSize(0.05)
#h_total_entries.SetMarkerSize(2)
#h_total_entries.Draw("hist text0")
#print("Raw total entries")
#canvas.Draw()
#canvas.SaveAs(f"{plots_dir}/total_entries.pdf")
#canvas.SaveAs(f"{plots_dir}/total_entries.png")


#exec(set_variable_defaults)
#variable = "mva_score_var10"
#title_x = "MVA Score"
#signal_scale_up = 10
#canvas_log_y = False
#exec(plot_mc_data)
#
#scale_y_axis = 10
#upper_pad_min_y = 0.1
#signal_scale_up = 1
#canvas_log_y = True
#exec(plot_mc_data)
#
#
#exec(set_variable_defaults)
#variable = "mva_score_var11"
#title_x = "MVA Score"
#signal_scale_up = 10
#canvas_log_y = False
#exec(plot_mc_data)
#
#scale_y_axis = 10
#upper_pad_min_y = 0.1
#signal_scale_up = 1
#canvas_log_y = True
#exec(plot_mc_data)
#
#

exec(set_variable_defaults)
if (len(args.vars) == 0):
    f = ROOT.TFile.Open(hist_filename)
    d = f.Get(hists_subdirectory)
    l = d.GetListOfKeys()
    h_names = []
    for i in l:
        name_ = i.GetName()
        if "data_obs_" in name_:
            h_names.append(name_.replace("data_obs_", ""))

    args.vars = h_names

print(f"hist file {hist_filename}, subdir {hists_subdirectory}, year {args.year}")
print(f"========================================================================")
print(args.vars)
print(f"========================================================================")

exec(set_variable_defaults)
variable = f"mva_score_{args.mva_type}"
title_x = f"MVA Score {args.mva_type}"
signal_scale_up = 10
canvas_log_y = False
if any(variable == i for i in args.vars): exec(plot_mc_data)

scale_y_axis = 50
upper_pad_min_y = 0.1
signal_scale_up = 1
canvas_log_y = True
if any(variable == i for i in args.vars): exec(plot_mc_data)

exec(set_variable_defaults)
variable = f"mva_score_{args.mva_type}_var1"
title_x = f"MVA Score {args.mva_type}"
signal_scale_up = 10
canvas_log_y = False
if any(variable == i for i in args.vars): exec(plot_mc_data)

scale_y_axis = 50
upper_pad_min_y = 0.1
signal_scale_up = 1
canvas_log_y = True
if any(variable == i for i in args.vars): exec(plot_mc_data)

exec(set_variable_defaults)
variable = f"mva_score_{args.mva_type}_var2"
title_x = f"MVA Score {args.mva_type}"
signal_scale_up = 10
canvas_log_y = False
if any(variable == i for i in args.vars): exec(plot_mc_data)

scale_y_axis = 50
upper_pad_min_y = 0.1
signal_scale_up = 1
canvas_log_y = True
if any(variable == i for i in args.vars): exec(plot_mc_data)

exec(set_variable_defaults)
variable = f"mva_score_{args.mva_type}_var3"
title_x = f"MVA Score {args.mva_type}"
signal_scale_up = 10
canvas_log_y = False
if any(variable == i for i in args.vars): exec(plot_mc_data)

scale_y_axis = 50
upper_pad_min_y = 0.1
signal_scale_up = 1
canvas_log_y = True
if any(variable == i for i in args.vars): exec(plot_mc_data)


exec(set_variable_defaults)
variable = "lep1_pt"
title_x = "p^{T}_{lep1}"
units = "GeV"
signal_scale_up = 10
canvas_log_y = False
if any(variable == i for i in args.vars): exec(plot_mc_data)


exec(set_variable_defaults)
variable = "lep1_eta"
title_x = "#eta_{lep1}"
signal_scale_up = 10
canvas_log_y = False
if any(variable == i for i in args.vars): exec(plot_mc_data)


exec(set_variable_defaults)
variable = "lep1_phi"
title_x = "#phi_{lep1}"
signal_scale_up = 10
canvas_log_y = False
if any(variable == i for i in args.vars): exec(plot_mc_data)


exec(set_variable_defaults)
variable = "lep2_pt"
title_x = "p^{T}_{lep2}"
units = "GeV"
signal_scale_up = 10
canvas_log_y = False
if any(variable == i for i in args.vars): exec(plot_mc_data)


exec(set_variable_defaults)
variable = "lep2_eta"
title_x = "#eta_{lep2}"
signal_scale_up = 10
canvas_log_y = False
if any(variable == i for i in args.vars): exec(plot_mc_data)


exec(set_variable_defaults)
variable = "lep2_phi"
title_x = "#phi_{lep2}"
signal_scale_up = 10
canvas_log_y = False
if any(variable == i for i in args.vars): exec(plot_mc_data)


exec(set_variable_defaults)
variable = "MET"
title_x = "MET"
units = "GeV"
signal_scale_up = 10
canvas_log_y = False
if any(variable == i for i in args.vars): exec(plot_mc_data)


exec(set_variable_defaults)
variable = "MET_phi"
title_x = "#phi_{MET}"
signal_scale_up = 10
canvas_log_y = False
if any(variable == i for i in args.vars): exec(plot_mc_data)

exec(set_variable_defaults)
variable = "nBtag_loose"
title_x = "nBtag_loose"
signal_scale_up = 10
canvas_log_y = False
if any(variable == i for i in args.vars): exec(plot_mc_data)

exec(set_variable_defaults)
variable = "nJet30"
title_x = "nJet30"
signal_scale_up = 10
canvas_log_y = False
if any(variable == i for i in args.vars): exec(plot_mc_data)


exec(set_variable_defaults)
variable = "fatjet_m"
title_x = "m_{V}"
units = "GeV"
signal_scale_up = 10
canvas_log_y = False
if any(variable == i for i in args.vars): exec(plot_mc_data)


exec(set_variable_defaults)
draw_with_ratio = False
variable = "fatjet_pt"
title_x = "p^{T}_{V}"
units = "GeV"
#ndivisions_x = 505
signal_scale_up = 10
canvas_log_y = False
if any(variable == i for i in args.vars): exec(plot_mc_data)


exec(set_variable_defaults)
variable = "fatjet_eta"
title_x = "#eta_{V}"
signal_scale_up = 10
canvas_log_y = False
if any(variable == i for i in args.vars): exec(plot_mc_data)


exec(set_variable_defaults)
variable = "fatjet_phi"
title_x = "#phi_{V}"
signal_scale_up = 10
canvas_log_y = False
if any(variable == i for i in args.vars): exec(plot_mc_data)


exec(set_variable_defaults)
variable = "fatjet_tau21"
title_x = "#tau_{21} (V)"
signal_scale_up = 10
canvas_log_y = False
if any(variable == i for i in args.vars): exec(plot_mc_data)

exec(set_variable_defaults)
variable = "dijet_m"
title_x = "m_{JJ}"
units = "GeV"
signal_scale_up = 10
canvas_log_y = False
if any(variable == i for i in args.vars): exec(plot_mc_data)


exec(set_variable_defaults)
variable = "dijet_pt"
title_x = "p^{T}_{JJ}"
units = "GeV"
signal_scale_up = 10
canvas_log_y = False
if any(variable == i for i in args.vars): exec(plot_mc_data)


exec(set_variable_defaults)
variable = "dijet_eta"
title_x = "#eta_{JJ}"
signal_scale_up = 10
canvas_log_y = False
if any(variable == i for i in args.vars): exec(plot_mc_data)


exec(set_variable_defaults)
variable = "dijet_j1_pt"
title_x = "p^{T}_{J1}"
units = "GeV"
signal_scale_up = 10
canvas_log_y = False
if any(variable == i for i in args.vars): exec(plot_mc_data)


exec(set_variable_defaults)
variable = "dijet_j2_pt"
title_x = "p^{T}_{J2}"
units = "GeV"
signal_scale_up = 10
canvas_log_y = False
if any(variable == i for i in args.vars): exec(plot_mc_data)


exec(set_variable_defaults)
variable = "dijet_j1_eta"
title_x = "#eta_{J1}"
signal_scale_up = 10
canvas_log_y = False
if any(variable == i for i in args.vars): exec(plot_mc_data)


exec(set_variable_defaults)
variable = "dijet_j2_eta"
title_x = "#eta_{J2}"
signal_scale_up = 10
canvas_log_y = False
if any(variable == i for i in args.vars): exec(plot_mc_data)


exec(set_variable_defaults)
variable = "v_lep_pt"
title_x = "p^{T}_{Z}" if args.boson == "Z" else "p^{T}_{W}"
units = "GeV"
signal_scale_up = 10
canvas_log_y = False
if any(variable == i for i in args.vars): exec(plot_mc_data)

scale_y_axis = 50
upper_pad_min_y = 0.1
signal_scale_up = 1
canvas_log_y = True
if any(variable == i for i in args.vars): exec(plot_mc_data)


exec(set_variable_defaults)
variable = "v_lep_eta"
title_x = "#eta_{Z}" if args.boson == "Z" else "#eta_{W}"
signal_scale_up = 10
canvas_log_y = False
if any(variable == i for i in args.vars): exec(plot_mc_data)

exec(set_variable_defaults)
variable = "v_lep_m"
title_x = "m_{Z}" if args.boson == "Z" else "m_{W}"
units = "GeV"
signal_scale_up = 10
canvas_log_y = False
if any(variable == i for i in args.vars): exec(plot_mc_data)

exec(set_variable_defaults)
variable = "v_lep_mt"
title_x = "m^{T}_{Z}" if args.boson == "Z" else "m^{T}_{W}"
units = "GeV"
signal_scale_up = 10
canvas_log_y = False
if any(variable == i for i in args.vars): exec(plot_mc_data)


exec(set_variable_defaults)
variable = "vbf_j1_pt"
title_x = "p^{T}_{j1}"
units = "GeV"
signal_scale_up = 10
canvas_log_y = False
if any(variable == i for i in args.vars): exec(plot_mc_data)


exec(set_variable_defaults)
variable = "vbf_j2_pt"
title_x = "p^{T}_{j2}"
units = "GeV"
signal_scale_up = 10
canvas_log_y = False
if any(variable == i for i in args.vars): exec(plot_mc_data)


exec(set_variable_defaults)
variable = "vbf_j1_eta"
title_x = "#eta_{j1}"
signal_scale_up = 10
canvas_log_y = False
if any(variable == i for i in args.vars): exec(plot_mc_data)


exec(set_variable_defaults)
variable = "vbf_j2_eta"
title_x = "#eta_{j2}"
signal_scale_up = 10
canvas_log_y = False
if any(variable == i for i in args.vars): exec(plot_mc_data)


exec(set_variable_defaults)
variable = "vbf_jj_Deta"
title_x = "|#Delta#eta_{jj}|"
signal_scale_up = 10
canvas_log_y = False
if any(variable == i for i in args.vars): exec(plot_mc_data)


exec(set_variable_defaults)
variable = "vbf_j1_phi"
title_x = "#phi_{j1}"
signal_scale_up = 10
canvas_log_y = False
if any(variable == i for i in args.vars): exec(plot_mc_data)


exec(set_variable_defaults)
variable = "vbf_j2_phi"
title_x = "#phi_{j2}"
signal_scale_up = 10
canvas_log_y = False
if any(variable == i for i in args.vars): exec(plot_mc_data)


exec(set_variable_defaults)
variable = "vbf_j1_qgid"
title_x = "VBS_{j1} QGL"
signal_scale_up = 10
canvas_log_y = False
if any(variable == i for i in args.vars): exec(plot_mc_data)


exec(set_variable_defaults)
variable = "vbf_j2_qgid"
title_x = "VBS_{j2} QGL"
signal_scale_up = 10
canvas_log_y = False
if any(variable == i for i in args.vars): exec(plot_mc_data)


exec(set_variable_defaults)
variable = "vbf_jj_m"
title_x = "m_{jj}"
units = "GeV"
signal_scale_up = 10
canvas_log_y = False
if any(variable == i for i in args.vars): exec(plot_mc_data)


exec(set_variable_defaults)
variable = "boson_centrality"
title_x = "Boson Centrality"
signal_scale_up = 10
canvas_log_y = False
if any(variable == i for i in args.vars): exec(plot_mc_data)


exec(set_variable_defaults)
variable = "zeppenfeld_lep_deta"
title_x = "Zeppenfeld* Z" if args.boson == "Z" else "Zeppenfeld* W"
signal_scale_up = 10
canvas_log_y = False
if any(variable == i for i in args.vars): exec(plot_mc_data)


exec(set_variable_defaults)
variable = "zeppenfeld_had_deta"
title_x = "Zeppenfeld* V"
signal_scale_up = 10
canvas_log_y = False
if any(variable == i for i in args.vars): exec(plot_mc_data)


exec(set_variable_defaults)
variable = "vv_m"
title_x = "m_{ZV}" if args.boson == "Z" else "m_{WV}"
units = "GeV"
signal_scale_up = 10
canvas_log_y = False
if any(variable == i for i in args.vars): exec(plot_mc_data)


exec(set_variable_defaults)
variable = "vv_mt"
title_x = "m^{T}_{ZV}" if args.boson == "Z" else "m^{T}_{WV}"
units = "GeV"
signal_scale_up = 10
canvas_log_y = False
if any(variable == i for i in args.vars): exec(plot_mc_data)


exec(set_variable_defaults)
variable = "vv_pt"
title_x = "p^{T}_{ZV}" if args.boson == "Z" else "p^{T}_{WV}"
units = "GeV"
signal_scale_up = 10
canvas_log_y = False
if any(variable == i for i in args.vars): exec(plot_mc_data)


exec(set_variable_defaults)
variable = "vv_eta"
title_x = "#eta_{ZV}" if args.boson == "Z" else "#eta_{WV}"
signal_scale_up = 10
canvas_log_y = False
if any(variable == i for i in args.vars): exec(plot_mc_data)


exec(set_variable_defaults)
variable = "vv_phi"
title_x = "#phi_{ZV}" if args.boson == "Z" else "#phi_{WV}"
signal_scale_up = 10
canvas_log_y = False
if any(variable == i for i in args.vars): exec(plot_mc_data)

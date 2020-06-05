#!/usr/bin/env python3

import ROOT
ROOT.gROOT.SetBatch()
ROOT.PyConfig.IgnoreCommandLineOptions = True
from pyroot_cms_scripts import CMS_style
import os
import argparse
ROOT.gErrorIgnoreLevel = ROOT.kError

parser = argparse.ArgumentParser()

parser.add_argument("-c", "--configs", action="append", help="tmva out folder(s) name")
parser.add_argument("-r", "--rebin", type=int, help="rebin BDT score out", default=1)

args = parser.parse_args()

configs = args.configs

bdt_files = {c: ROOT.TFile.Open(f"{c}/tmva_output.root") for c in configs}

plots_dir = "tmva_plots"

bdt_outputs = {c: f.Get(f"{c}/Method_BDT/BDT") for c, f in bdt_files.items()}

ROOT.gROOT.ForceStyle()
ROOT.gStyle.SetOptStat(0)
ROOT.gStyle.SetPalette(ROOT.kRainBow)

hists = {}
roc = {}
for c, f in bdt_outputs.items():
    hists[f"{c}_mva_s"] = f.Get("MVA_BDT_S")
    hists[f"{c}_mva_b"] = f.Get("MVA_BDT_B")
    hists[f"{c}_mva_s_train"] = f.Get("MVA_BDT_Train_S")
    hists[f"{c}_mva_b_train"] = f.Get("MVA_BDT_Train_B")

    roc[f"{c}_effBvsS"] = f.Get("MVA_BDT_effBvsS")
    roc[f"{c}_effBvsS_train"] = f.Get("MVA_BDT_trainingEffBvsS")

if args.rebin != 1:
    for hist in hists:
        hists[hist].Rebin(args.rebin)

draw_mva = """
CMS_style.cd()
canvas = ROOT.TCanvas("", "", 600, 600)
legend = ROOT.TLegend(0.55, 0.8, 0.93, 0.92, f"{c}")
legend.SetNColumns(3)
legend.SetTextFont(42)
legend.SetBorderSize(1)

hs = hists[f"{c}_mva_s"]
hst = hists[f"{c}_mva_s_train"]
ks_signal = hs.KolmogorovTest(hst, "X")
print(ks_signal)

hb = hists[f"{c}_mva_b"]
hbt = hists[f"{c}_mva_b_train"]
ks_bkg = hb.KolmogorovTest(hbt, "X")
print(ks_bkg)

hs.SetLineColor(ROOT.kBlue)
hs.SetFillColorAlpha(ROOT.kBlue, 0.5)
hs.SetFillStyle(1001)
hst.SetLineColor(ROOT.kBlue)
hst.SetMarkerColor(ROOT.kBlue)
hst.SetMarkerStyle(20)

hb.SetLineColor(ROOT.kRed)
hb.SetFillColorAlpha(ROOT.kRed, 0.5)
hb.SetFillStyle(1001)
hbt.SetLineColor(ROOT.kRed)
hbt.SetMarkerColor(ROOT.kRed)
hbt.SetMarkerStyle(20)

legend.AddEntry(hs, "Signal", "lf")
legend.AddEntry(hst, "Signal (Train)", "ep")
legend.AddEntry("", f"KS-S {ks_signal}", "")

legend.AddEntry(hb, "Bkg", "lf")
legend.AddEntry(hbt, "Bkg (Train)", "ep")
legend.AddEntry("", f"KS-B {ks_bkg}", "")

frame = max(hs, hst, hb, hbt, key=lambda x: x.GetMaximum()).Clone("frame")
frame.SetMaximum(1.4 * frame.GetMaximum())
frame.SetTitle(f"{c};BDT Score;")
frame.Draw("axis")

hs.Draw("hist same")
hst.Draw("x0 p same")
hb.Draw("hist same")
hbt.Draw("x0 p same")

legend.Draw()
canvas.Draw()
os.makedirs(f"{plots_dir}", exist_ok=True)
canvas.SaveAs(f"{plots_dir}/{c}.pdf")
canvas.SaveAs(f"{plots_dir}/{c}.png")
"""

for c in configs:
    exec(draw_mva)

draw_roc = """
CMS_style.cd()
canvas = ROOT.TCanvas()
frame = canvas.DrawFrame(0.0, 0.0, 1.0, 1.0, ";Sig Eff.;Bkg Eff.")
frame.Draw()
legend = ROOT.TLegend(0.18, 0.84 - 0.04*len(configs), 0.43, 0.92)
legend.SetTextFont(42)
legend.SetBorderSize(1)
for i, c in enumerate(configs):
    color = ROOT.gStyle.GetColorPalette(200*i)
    r = roc[f"{c}_effBvsS"]
    r.SetLineColor(color)
    r.Draw("same C")
    auc = 1 - (r.Integral()/100)
    legend.AddEntry(r, f"{c} ({auc:.3f})", "l")

    rt = roc[f"{c}_effBvsS_train"]
    rt.SetLineStyle(ROOT.kDashed)
    rt.SetLineColor(color)
    rt.Draw("same C")
    auc = 1 - (rt.Integral()/100)
    legend.AddEntry(rt, f"{c} ({auc:.3f}) (train)", "l")
legend.Draw()
canvas.SetLogy(0)
canvas.SetGrid()
canvas.Draw()
os.makedirs(f"{plots_dir}", exist_ok=True)
canvas.SaveAs(f"{plots_dir}/{'_'.join(c for c in configs)}_roc.pdf")
canvas.SaveAs(f"{plots_dir}/{'_'.join(c for c in configs)}_roc.png")
"""
exec(draw_roc)

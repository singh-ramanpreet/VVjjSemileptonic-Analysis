#!/usr/bin/env python3

import ROOT
import numpy as np
import argparse

parser = argparse.ArgumentParser()

parser.add_argument("--in-root", dest="in_root", type=str, default="2018_14Oct2020_zv.root")
parser.add_argument("--in-sub-dir", dest="in_sub_dir", type=str, default="sr_l")
parser.add_argument("--var-name", dest="var_name", type=str, default="mva_score_zv_var1")
parser.add_argument("--fit-root", dest="fit_root", type=str, default="datacards/fitDiagnostics.root")
parser.add_argument("--fit-sub-dir", dest="fit_sub_dir", type=str, default="shapes_fit_s/sig_reg")
parser.add_argument("--sub-dirname", dest="sub_dirname", type=str, default="sr_l_postfit")

args = parser.parse_args()

output = f"{args.in_root.rstrip('.root')}.{args.sub_dirname}.root"

in_hist_file = ROOT.TFile.Open(args.in_root)
h_data_obs = in_hist_file.Get(f"{args.in_sub_dir}/data_obs_{args.var_name}")
h_VBS_EWK = in_hist_file.Get(f"{args.in_sub_dir}/VBS_EWK_{args.var_name}")
h_VBS_QCD = in_hist_file.Get(f"{args.in_sub_dir}/VBS_QCD_{args.var_name}")
h_Top = in_hist_file.Get(f"{args.in_sub_dir}/Top_{args.var_name}")
h_DYJets = in_hist_file.Get(f"{args.in_sub_dir}/DYJets_HT_{args.var_name}")
h_WJets = in_hist_file.Get(f"{args.in_sub_dir}/WJets_HT_{args.var_name}")

h_Total_Bkg = h_VBS_EWK.Clone(f"Total_Bkg_{args.var_name}")
n_bins = h_VBS_EWK.GetNbinsX()


in_fit_file = ROOT.TFile.Open(args.fit_root)
fit_data = in_fit_file.Get(f"{args.fit_sub_dir}/data")
fit_VBS_EWK = in_fit_file.Get(f"{args.fit_sub_dir}/VBS_EWK")
fit_VBS_QCD = in_fit_file.Get(f"{args.fit_sub_dir}/VBS_QCD")
fit_Top = in_fit_file.Get(f"{args.fit_sub_dir}/Top")
fit_DYJets = in_fit_file.Get(f"{args.fit_sub_dir}/DYJets_HT")
fit_WJets = in_fit_file.Get(f"{args.fit_sub_dir}/WJets_HT")
fit_Total_Bkg = in_fit_file.Get(f"{args.fit_sub_dir}/total_background")

h_data_obs.Reset()
h_data_obs.SetBinErrorOption(ROOT.TH1.kPoisson)
h_VBS_EWK.Reset()
h_VBS_QCD.Reset()
h_Top.Reset()
h_DYJets.Reset()
h_WJets.Reset()
h_Total_Bkg.Reset()

for i in range(1, n_bins + 1):
    h_data_obs.SetBinContent(i, fit_data.GetPointY(i - 1))
    h_data_obs.SetBinError(i, fit_data.GetErrorY(i - 1))

    h_VBS_EWK.SetBinContent(i, fit_VBS_EWK.GetBinContent(i))
    h_VBS_EWK.SetBinError(i, fit_VBS_EWK.GetBinError(i))

    h_VBS_QCD.SetBinContent(i, fit_VBS_QCD.GetBinContent(i))
    h_VBS_QCD.SetBinError(i, fit_VBS_QCD.GetBinError(i))
    
    if type(fit_Top) != ROOT.TObject:
        h_Top.SetBinContent(i, fit_Top.GetBinContent(i))
        h_Top.SetBinError(i, fit_Top.GetBinError(i))

    if type(fit_DYJets) != ROOT.TObject:
        h_DYJets.SetBinContent(i, fit_DYJets.GetBinContent(i))
        h_DYJets.SetBinError(i, fit_DYJets.GetBinError(i))

    if type(fit_WJets) != ROOT.TObject:
        h_WJets.SetBinContent(i, fit_WJets.GetBinContent(i))
        h_WJets.SetBinError(i, fit_WJets.GetBinError(i))
    
    h_Total_Bkg.SetBinContent(i, fit_Total_Bkg.GetBinContent(i))
    h_Total_Bkg.SetBinError(i, fit_Total_Bkg.GetBinError(i))


out_hist_file = ROOT.TFile.Open(output, "recreate")
out_hist_file.mkdir(args.sub_dirname)
out_hist_file.cd(args.sub_dirname)

h_data_obs.Write()
h_VBS_EWK.Write()
h_VBS_QCD.Write()
h_Top.Write()
h_DYJets.Write()
h_WJets.Write()
h_Total_Bkg.Write()

out_hist_file.cd()
out_hist_file.Close()

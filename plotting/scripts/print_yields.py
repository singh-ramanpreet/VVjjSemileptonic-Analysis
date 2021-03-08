#!/usr/bin/env python3

import ROOT
ROOT.gROOT.SetBatch()
ROOT.PyConfig.IgnoreCommandLineOptions = True
import os
import argparse

parser = argparse.ArgumentParser()

parser.add_argument("-f", type=str, default="test.root")

args = parser.parse_args()

root_file = ROOT.TFile.Open(args.f)

list_of_keys = root_file.GetListOfKeys()

for i in list_of_keys:
    if all(j != i.GetName().rstrip() for j in ["sr1_l"]): continue
    tdir = root_file.Get(i.GetName())
    if tdir.ClassName() != "TDirectoryFile": continue
    print(tdir.GetName())
    h_data_yield = tdir.Get("data_obs_lep1_pt")
    if type(h_data_yield) == ROOT.TObject: continue
    data_yield= h_data_yield.Integral()
    mc_yield = (
        f"{tdir.Get('VBS_EWK_lep1_pt').Integral():.2f}",
        f"{tdir.Get('VBS_QCD_lep1_pt').Integral():.2f}",
        f"{tdir.Get('Top_lep1_pt').Integral():.2f}",
        f"{tdir.Get('DYJets_HT_lep1_pt').Integral():.2f}",
    )
    sig_yield = tdir.Get("VBS_EWK_lep1_pt").Integral()

    print("/".join(str(i) for i in mc_yield))
    #print(f"{data_yield:.0f}/{mc_yield}/{sig_yield:.2f}")
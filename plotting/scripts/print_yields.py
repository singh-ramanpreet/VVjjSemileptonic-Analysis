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
    if all(j != i.GetName().rstrip() for j in ["cr_vjets_e", "cr_vjets_m", "sr_e", "sr_m"]): continue
    tdir = root_file.Get(i.GetName())
    if tdir.ClassName() != "TDirectoryFile": continue
    print(tdir.GetName())
    h_data_yield = tdir.Get("data_obs_lept1_pt")
    if type(h_data_yield) == ROOT.TObject: continue
    data_yield= h_data_yield.Integral()
    mc_yield = (
        tdir.Get("VBS_QCD_lept1_pt").Integral() +
        tdir.Get("Top_lept1_pt").Integral() +
        tdir.Get("DYJets_HT_lept1_pt").Integral()
    )
    sig_yield = tdir.Get("VBS_EWK_lept1_pt").Integral()

    print(f"{data_yield:.0f}/{mc_yield:.0f}/{sig_yield:.2f}")
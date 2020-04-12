#!/usr/bin/env python3

import ROOT
ROOT.PyConfig.IgnoreCommandLineOptions = True
import sys

infile = ROOT.TFile.Open(sys.argv[1])
outfile = ROOT.TFile.Open(sys.argv[2], "update")
outfile.cd()

list_of_histograms = infile.GetListOfKeys()

cr = sys.argv[3]
outfile.mkdir(cr)
outfile.cd(f"/{cr}")

for hist in list_of_histograms:
    name = hist.GetName()
    
    if "mva_score" in name:
        print(name)
        get_hist = infile.Get(name)
        get_hist.Rebin(get_hist.GetNbinsX())
        print(get_hist.Integral())
        get_hist.Write()

outfile.Write()
outfile.Close()

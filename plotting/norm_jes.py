#!/usr/bin/env python3

import ROOT
ROOT.PyConfig.IgnoreCommandLineOptions = True
import sys

infile = ROOT.TFile.Open(sys.argv[1], "update")

infile.cd()
list_of_histograms = infile.GetListOfKeys()

for hist in list_of_histograms:
    name = hist.GetName()
    if "mva_score" not in name: continue
    if ("WJets" in name) or ("Top" in name):
        print(name)

        norm_hist = infile.Get(name)
        jesUp_hist = infile.Get(f"jesUp/{name}")
        jesDown_hist = infile.Get(f"jesDown/{name}")

        if jesUp_hist.Integral() != 0.0:
            normUp = (norm_hist.Integral()) / (jesUp_hist.Integral())
        else:
            normUp = 1.0

        if jesDown_hist.Integral() != 0.0:
            normDown = (norm_hist.Integral()) / (jesDown_hist.Integral())
        else:
            normDown = 1.0

        jesUp_hist.Scale(normUp)
        jesDown_hist.Scale(normDown)

        infile.cd()
        infile.cd("jesUp")
        jesUp_hist.Write()

        infile.cd()
        infile.cd("jesDown")
        jesDown_hist.Write()

infile.Write()
infile.Close()

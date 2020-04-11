#!/usr/bin/env python3

import ROOT
ROOT.PyConfig.IgnoreCommandLineOptions = True
import sys

infile = ROOT.TFile.Open(sys.argv[1], "update")

infile.cd()
list_of_histograms = infile.GetListOfKeys()

infile.mkdir("jesNormDown")
infile.mkdir("jesNormUp")

for hist in list_of_histograms:
    name = hist.GetName()
    if "mva_score" not in name: continue

    norm_hist = infile.Get(name)
    jesUp_hist = infile.Get(f"jesUp/{name}")
    jesDown_hist = infile.Get(f"jesUp/{name}")

    jesUp_normalized = jesUp_hist.Clone(name)
    jesDown_normalized = jesDown_hist.Clone(name)

    if jesUp_hist.Integral() != 0.0:
        normUp = (norm_hist.Integral()) / (jesUp_hist.Integral())
    else:
        normUp = 1.0

    if jesDown_hist.Integral() != 0.0:
        normDown = (norm_hist.Integral()) / (jesDown_hist.Integral())
    else:
        normDown = 1.0

    jesUp_normalized.Scale(normUp)
    jesDown_normalized.Scale(normDown)

    infile.cd()
    infile.cd("jesNormUp")
    jesUp_normalized.Write()

    infile.cd()
    infile.cd("jesNormDown")
    jesDown_normalized.Write()

infile.ls("*")

infile.Write()
infile.Close()

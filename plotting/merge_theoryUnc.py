#!/usr/bin/env python3

import ROOT
ROOT.PyConfig.IgnoreCommandLineOptions = True
import sys

infile = ROOT.TFile.Open(sys.argv[1])
outfile = ROOT.TFile.Open(sys.argv[2], "update")
outfile.cd()

list_of_histograms = infile.GetListOfKeys()

for i in ["qcd_scaleUp", "qcd_scaleDown", "pdf_scaleUp", "pdf_scaleDown"]:
    outfile.mkdir(i)
    outfile.cd(f"/{i}")

    for j in ["VBS_EWK", "VBS_QCD"]:

        for hist in list_of_histograms:
            name = hist.GetName()

            if (j in name) and (i in name):

                if "pdf" in i: new_name = name.split("_pdf_")[0]
                if "qcd" in i: new_name = name.split("_qcd_")[0]

                print(name)
                get_hist = infile.Get(name)
                get_hist.SetName(new_name)
                get_hist.Write()

outfile.Write()
outfile.Close()

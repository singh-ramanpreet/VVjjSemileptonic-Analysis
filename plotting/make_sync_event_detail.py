#!/usr/bin/env python3

import subprocess
import json
import argparse
from collections import OrderedDict
import ROOT
ROOT.PyConfig.IgnoreCommandLineOptions = True
ROOT.gROOT.SetBatch(ROOT.kTRUE)

parser = argparse.ArgumentParser()

parser.add_argument("--infile", type=str, default="root://cmseos.fnal.gov//store/user/rsingh/wv_vbs_ntuples/WVJJTree_2021_Apr_21/2016/Data_noDup_D.root",
                    help="reference root file, default=%(default)s")

parser.add_argument("--debug", action="store_true",
                    help="default=%(default)s")

parser.add_argument("--outdir", type=str, default="detailed_sync",
                    help="detailed sync out dir, default=%(default)s")

args = parser.parse_args()

mk_outdir = subprocess.Popen(["mkdir", "-p", args.outdir])
mk_outdir.wait()

cuts = {
    "zv": [
        "!isAntiIso && lep2_pt > 0 && bos_PuppiAK8_pt > 0",
        "lep1_pt > 20",
        "lep2_pt > 20",
        "(lep1_m > 0.105 && fabs(lep1_eta) < 2.4 && fabs(lep2_eta) < 2.4) || (lep1_m < 0.105 && fabs(lep1_eta) < 2.5 && !(fabs(lep1_eta) > 1.4442 && fabs(lep1_eta) < 1.566) && fabs(lep2_eta) < 2.5 && !(fabs(lep2_eta) > 1.4442 && fabs(lep2_eta) < 1.566))",
        "dilep_m > 76 && dilep_m < 106",
        "bos_PuppiAK8_pt > 200",
        "fabs(bos_PuppiAK8_eta) < 2.4",
        "vbf_deta > 2.5",
        "(bos_PuppiAK8_m_sd0_corr > 40 && bos_PuppiAK8_m_sd0_corr < 65) || (bos_PuppiAK8_m_sd0_corr > 105 && bos_PuppiAK8_m_sd0_corr < 150)"
    ],
    "zjj": [
        "!isAntiIso && lep2_pt > 0 && bos_AK4AK4_pt > 0 && bos_PuppiAK8_pt < 0",
        "lep1_pt > 20",
        "lep2_pt > 20",
        "(lep1_m > 0.105 && fabs(lep1_eta) < 2.4 && fabs(lep2_eta) < 2.4) || (lep1_m < 0.105 && fabs(lep1_eta) < 2.5 && !(fabs(lep1_eta) > 1.4442 && fabs(lep1_eta) < 1.566) && fabs(lep2_eta) < 2.5 && !(fabs(lep2_eta) > 1.4442 && fabs(lep2_eta) < 1.566))",
        "dilep_m > 76 && dilep_m < 106",
        "bos_j1_AK4_pt > 30 && bos_j2_AK4_pt > 30",
        "vbf_deta > 2.5",
        "(bos_AK4AK4_m > 40 && bos_AK4AK4_m < 65) || (bos_AK4AK4_m > 105 && bos_AK4AK4_m < 150)"
    ]
}

vars_to_print = {
    "zv": [
        "run", "evt",
        "lep1_pt", "lep2_pt", "lep1_eta", "lep2_eta", "dilep_m",
        "bos_PuppiAK8_pt", "bos_PuppiAK8_eta", "bos_PuppiAK8_tau2tau1",
        "vbf1_AK4_pt", "vbf2_AK4_pt", "vbf1_AK4_eta", "vbf2_AK4_eta",
        "vbf_m", "vbf_deta", "bos_PuppiAK8_m_sd0_corr", "nBtag_loose", "lep1_m"
    ],
    "zjj": [
        "run", "evt",
        "lep1_pt", "lep2_pt", "lep1_eta", "lep2_eta", "dilep_m",
        "vbf1_AK4_pt", "vbf2_AK4_pt", "vbf1_AK4_eta", "vbf2_AK4_eta",
        "bos_j1_AK4_pt", "bos_j2_AK4_pt", "bos_j1_AK4_eta", "bos_j2_AK4_eta",
        "vbf_m", "vbf_deta", "bos_AK4AK4_m", "nBtag_loose", "lep1_m"
    ]
}

output_csv = {
    x: {
        "file": args.outdir + "/" + x + ".csv",
        "cut": "(" + ") && (".join(cuts[x]) + ")",
        "vars": vars_to_print[x]
    }
    for x in cuts
}

for x in output_csv:
    file_ = ROOT.TFile.Open(args.infile)
    events = file_.Get("Events")
    selected_tree = events.CopyTree(output_csv[x]["cut"])
    print(selected_tree.GetEntries())
    f = open(output_csv[x]["file"], "w")
    for i,event in enumerate(selected_tree):
        if i == 0:
            print(",".join(output_csv[x]["vars"]), file=f)
        print(",".join([f"{events.__getattr__(v):.2f}" for v in output_csv[x]["vars"]]), file=f)

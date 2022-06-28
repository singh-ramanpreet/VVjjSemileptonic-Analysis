#!/usr/bin/env python3

import subprocess
import json
import argparse
from collections import OrderedDict
import ROOT
ROOT.PyConfig.IgnoreCommandLineOptions = True
ROOT.gROOT.SetBatch(ROOT.kTRUE)

parser = argparse.ArgumentParser()

parser.add_argument("--datasets", type=str, default="../datasets_2016.json",
                    help="json file: info of datasets, default=%(default)s")

parser.add_argument("--location", type=str, default="/store/user/rsingh/wv_vbs_ntuples/WVJJTree_2021_Mar_07/2016",
                    help="eos directory location, default=%(default)s")

parser.add_argument("--debug", action="store_true",
                    help="default=%(default)s")

parser.add_argument("--outdir", type=str, default="cutflows",
                    help="cutflows out dir, default=%(default)s")

args = parser.parse_args()

samples_dict = json.load(open(args.datasets, "r"))

mk_outdir = subprocess.Popen(["mkdir", "-p", args.outdir])
mk_outdir.wait()

cuts = {
    "zv": [
        "!isAntiIso && lep2_pt > 0 && bos_PuppiAK8_pt > 0",
        "lep1_pt > 25",
        "lep2_pt > 20",
        "lep1_q * lep2_q < 0",
        "(lep1_m > 0.105 && fabs(lep1_eta) < 2.4 && fabs(lep2_eta) < 2.4) || (lep1_m < 0.105 && fabs(lep1_eta) < 2.5 && !(fabs(lep1_eta) > 1.4442 && fabs(lep1_eta) < 1.566) && fabs(lep2_eta) < 2.5 && !(fabs(lep2_eta) > 1.4442 && fabs(lep2_eta) < 1.566))",
        "dilep_m > 75 && dilep_m < 105",
        "bos_PuppiAK8_pt > 200",
        "fabs(bos_PuppiAK8_eta) < 2.4",
        "bos_PuppiAK8_tau2tau1 < 0.45",
        "vbf_m > 500",
        "vbf1_AK4_pt > 50 && vbf2_AK4_pt > 50",
        "vbf_deta > 2.5",
        "bos_PuppiAK8_m_sd0_corr > 65 && bos_PuppiAK8_m_sd0_corr < 105",
        "nBtag_loose == 0"
    ],
    "zjj": [
        "!isAntiIso && lep2_pt > 0 && bos_AK4AK4_pt > 0",
        "lep1_pt > 25",
        "lep2_pt > 20",
        "lep1_q * lep2_q < 0",
        "(lep1_m > 0.105 && fabs(lep1_eta) < 2.4 && fabs(lep2_eta) < 2.4) || (lep1_m < 0.105 && fabs(lep1_eta) < 2.5 && !(fabs(lep1_eta) > 1.4442 && fabs(lep1_eta) < 1.566) && fabs(lep2_eta) < 2.5 && !(fabs(lep2_eta) > 1.4442 && fabs(lep2_eta) < 1.566))",
        "dilep_m > 75 && dilep_m < 105",
        "bos_j1_AK4_pt > 30 && bos_j2_AK4_pt > 30",
        "vbf_m > 500",
        "vbf1_AK4_pt > 50 && vbf2_AK4_pt > 50",
        "vbf_deta > 2.5",
        "bos_AK4AK4_m > 65 && bos_AK4AK4_m < 105",
        "nBtag_loose == 0"
    ]
}

cutflow_hist = {x: ROOT.TH1F(x + "FullCutFlow", x + "FullCutFlow", len(cuts[x]), 0, len(cuts[x])) for x in cuts}
for channel in cuts:
    for i,cut in enumerate(cuts[channel]):
        cutflow_hist[channel].GetXaxis().SetBinLabel(i+1, cut)

output_csv = {
    x: {
        "file": args.outdir + "/" + x + ".csv",
        "cuts": OrderedDict()
    }
    for x in cuts
}

for key in samples_dict:

    filelist = samples_dict[key]["filelist"]
    #lumi = samples_dict[key]["lumi"]
    
    if key == "data_obs": continue

    print("\n")
    print(args.location)
    print("Sample Tag: ", key)
    print("====================================================================")
    for i, sample in enumerate(filelist):

        sample_full = args.location + "/" + sample["name"]

        root_file_ls = subprocess.Popen(["eos", "root://cmseos.fnal.gov", "ls", f"{sample_full}_*.root"], stdout=subprocess.PIPE)
        stdout = root_file_ls.communicate()[0]
        root_files = [
            f"root://cmseos.fnal.gov/{args.location}/{i}" for i in stdout.strip().decode("ascii").split("\n")
        ]

        hadd = subprocess.Popen(["hadd", "-f", "-T", "htemp.root"] + root_files,
                                stdout=subprocess.DEVNULL if not args.debug else None,
                                stderr=subprocess.STDOUT if not args.debug else None)
        hadd.wait()

        f_htemp = ROOT.TFile.Open("htemp.root")

        htemp_0 = f_htemp.Get("TotalCutFlow")
        output = ROOT.TFile.Open(args.outdir + "/" + sample["name"] + ".root", "recreate")
        htemp_0.Write()

        for channel in cuts:
            htemp_1 = f_htemp.Get(channel + "CutFlow")
            htemp_2 = cutflow_hist[channel].Clone()

            for root_file in root_files:
                file_ = ROOT.TFile.Open(root_file)
                events = file_.Get("Events")
                for i, cut in enumerate(cuts[channel]):
                    n = int(events.GetEntries("(" + ") && (".join(cuts[channel][:i+1]) + ")"))
                    htemp_2.Fill(cut, n)

            output.cd()
            htemp_1.Write()
            htemp_2.Write()

            if not bool(output_csv[channel]["cuts"]):
                output_csv[channel]["cuts"]["header"] = ["Cuts"]
                output_csv[channel]["cuts"]["xs"] = ["xs"]
                output_csv[channel]["cuts"]["lumi"] = ["lumi"]

                for bin1_ in range(1, htemp_1.GetNbinsX() + 1):
                    output_csv[channel]["cuts"][bin1_] = [htemp_1.GetXaxis().GetBinLabel(bin1_)]

                for bin2_ in range(1, htemp_2.GetNbinsX() + 1):
                    output_csv[channel]["cuts"][bin1_ + bin2_] = [htemp_2.GetXaxis().GetBinLabel(bin2_)]

            output_csv[channel]["cuts"]["header"].append(sample["name"])
            output_csv[channel]["cuts"]["xs"].append(str(sample["xs"]))
            output_csv[channel]["cuts"]["lumi"].append(str(samples_dict[key]["lumi"]))

            for bin1_ in range(1, htemp_1.GetNbinsX() + 1):
                output_csv[channel]["cuts"][bin1_].append(str(htemp_1.GetBinContent(bin1_)))
            for bin2_ in range(1, htemp_2.GetNbinsX() + 1):
                output_csv[channel]["cuts"][bin1_ + bin2_].append(str(htemp_2.GetBinContent(bin2_)))

            with open(output_csv[channel]["file"], "w") as f:
                for k in output_csv[channel]["cuts"]:
                    print(",".join(output_csv[channel]["cuts"][k]), file=f)


    print("====================================================================")

cleanup = subprocess.Popen(["rm", "-v", "htemp.root"])
cleanup.wait()

#!/usr/bin/env python3

import subprocess
import json
import argparse
import ROOT


parser = argparse.ArgumentParser()

parser.add_argument("--datasets", type=str, default="datasets_2016.json",
                    help="json file: info of datasets, default=%(default)s")

parser.add_argument("--location", type=str, default="/store/user/rsingh/wv_vbs_ntuples/WVJJTree_2020_Dec_12/2016",
                    help="eos directory location, default=%(default)s")

parser.add_argument("--debug", action="store_true",
                    help="default=%(default)s")

parser.add_argument("--sample-tag", dest="sample_tag", type=str, default="all",
                    help="sample tag to process from json file, default=%(default)s")

args = parser.parse_args()

samples_dict = json.load(open(args.datasets, "r"))

for key in samples_dict:

    if args.sample_tag != "all" and args.sample_tag != key: continue

    filelist = samples_dict[key]["filelist"]
    lumi = samples_dict[key]["lumi"]

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
        htemp = f_htemp.Get("TotalEvents")
        nMC_from_hist = htemp.GetBinContent(2)

        xs = sample["xs"]
        nMC = 0
        kf = 1.0

        if "nMC" in sample.keys(): nMC = sample["nMC"]
        if "kf" in sample.keys(): kf = sample["kf"]

        #print(f"{sample['name']}, \"xs\": {xs} , \"nMC\": {nMC_from_hist}")
        print("Sample: ", sample["name"])
        print("XS: ", xs)
        print("k-factor: ", kf)
        print("nMC(in json):   ", nMC)
        print("nMC(from hist): ", nMC_from_hist)
    print("====================================================================")

cleanup = subprocess.Popen(["rm", "-v", "htemp.root"])
cleanup.wait()

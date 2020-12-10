#!/usr/bin/env python3

import argparse
import os
import sys
import json
import ROOT

from collections import OrderedDict

ROOT.PyConfig.IgnoreCommandLineOptions = True
ROOT.gROOT.SetBatch(ROOT.kTRUE)

parser = argparse.ArgumentParser()

parser.add_argument("-f", type=str, default="",
                    help="input test root file, default=%(default)s")

parser.add_argument("-y", type=str, default="2016",
                    help="input test root file year, default=%(default)s")

parser.add_argument("-s", type=str, default="../systematics_map.json",
                    help="json file: systematic map per channel, default=%(default)s")

parser.add_argument("-c", type=str, default="zv",
                    help="name of channel: wjj, wv, zjj, zv, default=%(default)s")

parser.add_argument("-o", type=str, default="sys_test.root",
                    help="output hist file, default=%(default)s")

args = parser.parse_args()

# systematics map
systematics_map = OrderedDict(json.load(open(args.s, "r")))

tfile = ROOT.TFile.Open(args.f)
ttree = tfile.Get("Events")

if args.c == "zv":
     cut = "lep2_pt > 0 && bos_PuppiAK8_m_sd0_corr > 0"

elif args.c == "wv":
     cut = "lep2_pt < 0 && bos_PuppiAK8_m_sd0_corr > 0"

elif args.c == "zjj":
     cut = "lep2_pt > 0 && bos_AK4AK4_m > 0"

elif args.c == "wjj":
     cut = "lep2_pt < 0 && bos_AK4AK4_m > 0"

else:
    print("select correct channel")
    sys.exit()

tfile_out = ROOT.TFile.Open(args.o, "update")
tfile_out.cd()

systematics = list(systematics_map[args.c].keys())

for sys in [""] + systematics:
    print(sys)
    if sys != "":
        variables = systematics_map[args.c][sys]
    else:
        variables = list(set(i for s in systematics for i in systematics_map[args.c][s]))
    tfile_out.mkdir(f"{args.y}_{args.c}{sys}", "", ROOT.kTRUE)
    tfile_out.cd(f"{args.y}_{args.c}{sys}")
    for var in variables:
        ttree.Draw(var + sys, cut)
        htemp = ROOT.gPad.GetPrimitive("htemp")
        htemp.Write(f"{var}", ROOT.gROOT.kOverwrite)
    tfile_out.cd()
tfile_out.Write()
tfile_out.Close()

sys_to_plot = [i for i in systematics if "Up" in i]
for sys in sys_to_plot:
    variables = systematics_map[args.c][sys]
    for var in variables:
        print(f"Making plots for {var} with {sys.strip('_').strip('Up')}")
        os.popen(f"./plot_sys.py -f {args.o} -d {args.y}_{args.c} -a {var} -s {sys.strip('_').strip('Up')}").read()

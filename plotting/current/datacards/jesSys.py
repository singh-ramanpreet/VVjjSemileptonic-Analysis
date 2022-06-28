#!/usr/bin/env python3

import ROOT
import numpy as np
import argparse

parser = argparse.ArgumentParser()

parser.add_argument("--in-root", dest="in_root", type=str, default="../2016_2021_Mar_04_zv.root")
parser.add_argument("--in-sub-dir", dest="in_sub_dir", type=str, default="sr1_l")
parser.add_argument("--var-name", dest="var_name", type=str, default="mva_score_zv_var1")

args = parser.parse_args()

sys_list = [
    "jesFlavorQCD",          
    "jesRelativeBal",        
    "jesHF",                 
    "jesBBEC1",              
    "jesEC2",                
    "jesAbsolute",           
    "jesBBEC1_Year",         
    "jesEC2_Year",           
    "jesAbsolute_Year",      
    "jesHF_Year",            
    "jesRelativeSample_Year"
]

processes = [
    "VBS_EWK",
    "DYJets_HT",
    "VBS_QCD",
    "Top"
]

in_hist_file = ROOT.TFile.Open(args.in_root)

string_print=""



for sys in sys_list:
    for i, process in enumerate(processes):
        central_integral = in_hist_file.Get(f"{args.in_sub_dir}/{process}_{args.var_name}").Integral()
        sys_integral_Down = in_hist_file.Get(f"{args.in_sub_dir}_{sys}Down/{process}_{args.var_name}").Integral()
        sys_integral_Up = in_hist_file.Get(f"{args.in_sub_dir}_{sys}Up/{process}_{args.var_name}").Integral()

        if i == 0:
            print(f"{sys:<28}{'lnN':<7}{sys_integral_Down/central_integral:.4f}/{sys_integral_Up/central_integral:.4f}", sep="", end="")
        else:
            print(f"{'':<4}{sys_integral_Down/central_integral:.4f}/{sys_integral_Up/central_integral:.4f}", sep="", end="")
    print("")

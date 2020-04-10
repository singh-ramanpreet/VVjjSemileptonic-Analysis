#!/usr/bin/env python3

import argparse
import ROOT
ROOT.PyConfig.IgnoreCommandLineOptions = True
import os
import json
import numpy as np
import awkward
import uproot
from pprint import pprint
from array import array
from root_numpy.tmva import evaluate_reader

parser = argparse.ArgumentParser()

parser.add_argument(
    "--datasets", type=str, default="../datasets_2016.json",
    help="json file: info of datasets, default=%(default)s"
    )

parser.add_argument(
    "--year", type=str, default="2016",
    help="dataset year, default=%(default)s"
    )

parser.add_argument(
    "--variables", type=str, default="../variables_map.json",
    help="json file: variables central and systematic map, default=%(default)s"
    )

parser.add_argument(
    "--systematic", type=str, default="central",
    help="variables point to given systematic, default=%(default)s"
    )

parser.add_argument(
    "--output", type=str, default="df_dataset.awkd",
    help="awkd file output name, default=%(default)s"
    )

parser.add_argument(
    "--suffix-out", dest="suffix_out", type=str, default="BDT",
    help="additional suffix in output filename, default=%(default)s"
    )

parser.add_argument(
    "--mva", type=str, default="",
    help="mva training weight file (xml), default=%(default)s"
    )

parser.add_argument(
    "--mva-var-list", dest="mva_vars", type=str, default="",
    help="mva training variable list, default=%(default)s"
    )

args = parser.parse_args()

# map variables to be used
print(f"Preparing data_frames for systematic '{args.systematic}'")

variables_mapped = {}
variables_map = json.load(open(args.variables, "r"))

for name_ in variables_map:
    systematic = args.systematic
    if systematic != "central":
        if systematic in variables_map[name_]:
            print(f"using systematic '{systematic}' for '{name_}'")
        else:
            systematic = "central"

    variables_mapped[name_] = variables_map[name_][systematic]

#pprint(variables_mapped, width=1)
ttree_branches = list(variables_mapped.values())

# TMVA Reader
if args.mva != "":
    mva_variables = open(args.mva_vars).readlines()
    mva_variables = [i.rstrip("\n") for i in mva_variables]

    mva_reader = ROOT.TMVA.Reader()

    for var in mva_variables:
        mva_reader.AddVariable(var, array("f", [-999.0]))

    mva_reader.BookMVA("BDT", args.mva)

# Loop over samples
dfs = {}
samples_dict = json.load(open(args.datasets, "r"))

for key in samples_dict:

    location = samples_dict[key]["location"]
    filelist = samples_dict[key]["filelist"]
    lumi = samples_dict[key]["lumi"]

    for sample in filelist:

        root_file = location + sample["name"]
        xs = sample["xs"]
        nMC = sample["nMC"]
        nMCneg = sample["nMCneg"]

        xs_weight = (lumi * xs) / (nMC - (2 * nMCneg))

        print("loading ... ", key, sample["name"])

        df = uproot.lazyarrays(root_file, "Events", branches=ttree_branches, persistvirtual=True)

        for new_name, var_name in variables_mapped.items():
            df[new_name] = df[var_name]
            if new_name != var_name:
                del df[var_name]

        # some derived columns
        df["vbf_jj_Deta"] = np.abs(df["vbf_j1_eta"] - df["vbf_j2_eta"])
        df["fatjet_n2b1"] = df["fatjet_e3_v2_sdb1"] / (df["fatjet_e2_sdb1"])**2
        df["fatjet_n2b2"] = df["fatjet_e3_v2_sdb2"] / (df["fatjet_e2_sdb2"])**2
        df["ht"] = df["fatjet_pt"] + df["vbf_j1_pt"] + df["vbf_j2_pt"]
        df["zeppenfeld_w_Deta"] = df["zeppenfeld_w"] / df["vbf_jj_Deta"]
        df["zeppenfeld_v_Deta"] = df["zeppenfeld_v"] / df["vbf_jj_Deta"]

        df["lept_channel"] = (df["lept1_m"] != 0.1056583745).astype(int)
        df["v_mt"] = np.sqrt(df["v_m"]**2 + df["v_pt"]**2)

        # till they are available
        df["trig_eff_weight"] = 1.0
        df["trig_eff_weight2"] = 1.0
        df["btag0_weight"] = 1.0

        if "data" in key:
            df["gen_weight"] = 1.0
            df["pu_weight"] = 1.0
            df["pu_weight_up"] = 1.0
            df["pu_weight_down"] = 1.0
            df["trig_eff_weight"] = 1.0
            df["trig_eff_weight2"] = 1.0
            df["id_eff_weight"] = 1.0
            df["id_eff_weight2"] = 1.0
            df["btag0_weight"] = 1.0

        if args.mva != "":
            var_data = np.column_stack(tuple([df[var] for var in mva_variables]))
            mva_score = evaluate_reader(mva_reader, "BDT", var_data)
            df["mva_score"] = mva_score
        else:
            df["mva_score"] = -999.0

        print(df["mva_score"][:5])

        dfs[f"{key}/{sample['name']}"] = {"xs_weight": xs_weight, "dframe": df}

output_filename = args.output
output_ = args.output.split(".awkd")[0]
output_ = f"{output_}_{args.year}"

if args.mva != "":
    mva_tag = f"_{args.suffix_out}"
else:
    mva_tag = ""

if args.systematic == "central":
    output_filename = f"{output_}{mva_tag}.awkd"
else:
    output_filename = f"{output_}_{args.systematic}{mva_tag}.awkd"

awkward.save(output_filename, dfs, mode="w")

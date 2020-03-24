#!/usr/bin/env python3

import argparse
import ROOT
import json
import numpy as np
import awkward
from array import array
from root_numpy.tmva import evaluate_reader

parser = argparse.ArgumentParser()

parser.add_argument(
    "--dframes", type=str, default="df_step1.awkd",
    help="awkd file: from step1, default=%(default)s"
    )

parser.add_argument(
    "--output", type=str, default="",
    help="awkd file output name, default=%(default)s"
    )


parser.add_argument(
    "--mva", type=str, default="",
    help="mva training weight file (xml), default=%(default)s"
    )

parser.add_argument(
    "--var_list", type=str, default="",
    help="mva training variable list, default=%(default)s"
    )

args = parser.parse_args()

variables = open(args.var_list).readlines()
variables = [i.rstrip("\n") for i in variables]

# TMVA Reader
mva_reader = ROOT.TMVA.Reader()

for var in variables:
    mva_reader.AddVariable(var, array("f", [-999.0]))

mva_reader.BookMVA("BDT", args.mva)

# Loop over dframes
dfs = awkward.load(args.dframes)
new_dfs = {}
for i in dfs:

    df = dfs[i]["dframe"]
    xs_weight = dfs[i]["xs_weight"]
    
    key = i.split("/")[0]
    filename = i.split("/")[1]

    print(key, filename)

    # add mva column
    df["mva_score"] = -999.0

    var_data = np.column_stack(tuple([df[var] for var in variables]))
    mva_score = evaluate_reader(mva_reader, "BDT", var_data)
    df["mva_score"] = mva_score

    print(df["mva_score"])

    new_dfs[f"{key}/{filename}"] = {"xs_weight": xs_weight, "dframe": df}

if args.output == "":
    output_filename = args.dframes.replace("step1", "step2")
else:
    output_filename = args.output

awkward.save(output_filename, new_dfs, mode="w")
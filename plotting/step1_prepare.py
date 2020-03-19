#!/usr/bin/env python3

import argparse
import ROOT
import json
import numpy as np
import awkward
import uproot
import importlib
from array import array
from root_numpy.tmva import evaluate_reader
import xml.etree.ElementTree as ET

parser = argparse.ArgumentParser()

parser.add_argument(
    "--datasets", type=str, default="../datasets_2016.json",
    help="json file containing info of datasets, default=%(default)s"
    )

parser.add_argument(
    "--output", type=str, default="data_frames.awkd",
    help="awkd file output name, default=%(default)s"
    )

parser.add_argument(
    "--mva", type=str, default="",
    help="mva training weight file (xml), default=%(default)s"
    )

args = parser.parse_args()

data_blind = True

samples_dict = json.load(open(args.datasets, "r"))

# TMVA Reader
if args.mva != "":
    xml_tree = ET.parse(args.mva)
    xml_nodes = xml_tree.getroot().getchildren()

    vars_node = xml_nodes[2]
    if vars_node.tag != "Variables":
        raise Exception("Check node index in xml file.")

    n_vars = vars_node.attrib["NVar"]
    vars_node = vars_node.getchildren()

    vars_label = [i.attrib["Label"] for i in vars_node]
    vars_exp = {i.attrib["Label"]: i.attrib["Expression"] for i in vars_node}
    vars_array = {i.attrib["Label"]: array("f", [-999.0]) for i in vars_node}

    mva_reader = ROOT.TMVA.Reader()

    for i_var in vars_label:
        mva_reader.AddVariable(f"{i_var} := {vars_exp[i_var]}", vars_array[i_var])

    mva_reader.BookMVA("BDT", args.mva)


# Loop over samples
dfs = {}
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

        df = uproot.lazyarrays(root_file, "otree", persistvirtual=True)

        if "isResolved" not in df.columns:
            df["isResolved"] = False

        if "data" in key:
            df["btag0Wgt"] = 1.0

        # add mva column
        df["mva_score"] = -999.0
        
        # some new columns
        df["ht"] = df["ungroomed_PuppiAK8_jet_pt"] + df["vbf_maxpt_j1_pt"] + df["vbf_maxpt_j2_pt"]
        df["ZeppenfeldWH_dEtajj"] = df["ZeppenfeldWH"] / df["vbf_maxpt_jj_Deta"]
        df["ZeppenfeldWL_dEtajj"] = df["ZeppenfeldWL_type0"] / df["vbf_maxpt_jj_Deta"]
        
        if data_blind and ("data" in key) and args.mva != "":
            print("skipping mva for data")

        elif args.mva != "":
            var_data = np.column_stack(tuple([df[i_var] for i_var in vars_label]))
            mva_score = evaluate_reader(mva_reader, "BDT", var_data)
            df["mva_score"] = mva_score

        print(df["mva_score"])

        dfs[f"{key}/{sample['name']}"] = {"xs_weight": xs_weight, "dframe": df}

awkward.save(args.output, dfs, mode="w")

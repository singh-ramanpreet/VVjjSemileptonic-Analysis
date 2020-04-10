#!/usr/bin/env python3

import sys
import os
import numpy as np
import ROOT
ROOT.PyConfig.IgnoreCommandLineOptions = True
import inspect
import awkward
import argparse
import importlib

parser = argparse.ArgumentParser()

parser.add_argument(
    "--dframes", type=str, default="df_dataset_2016.awkd",
    help="awkd file of datasets df prepared, default=%(default)s"
    )

parser.add_argument(
    "--region", type=str, default="train_wv_01",
    help="region , default=%(default)s"
    )

parser.add_argument(
    "--out-dir", dest="out_dir", type=str, default="BDTG",
    help="output directory for tmva, default=%(default)s"
    )

parser.add_argument(
    "--BDT-NTrees", dest="BDT_NTrees", type=str, default="100",
    help="BDT-Config, default=%(default)s"
    )

parser.add_argument(
    "--BDT-MinNodeSize", dest="BDT_MinNodeSize", type=str, default="10%",
    help="BDT-Config, default=%(default)s"
    )

parser.add_argument(
    "--BDT-MaxDepth", dest="BDT_MaxDepth", type=str, default="3",
    help="BDT-Config, default=%(default)s"
    )

parser.add_argument(
    "--BDT-nCuts", dest="BDT_nCuts", type=str, default="100",
    help="BDT-Config, default=%(default)s"
    )

parser.add_argument(
    "--BDT-Shrinkage", dest="BDT_Shrinkage", type=str, default="0.05",
    help="BDT-Config, default=%(default)s"
    )

parser.add_argument(
    "--BDT-BaggedFrac", dest="BDT_BaggedFrac", type=str, default="0.5",
    help="BDT-Config, default=%(default)s"
    )

args = parser.parse_args()


dfs = awkward.load(args.dframes)

keys = list(dfs.keys())
sigs = [i for i in keys if "VBS_EWK/" in i]
bkgs1 = [i for i in keys if "WJets/" in i]
bkgs2 = [i for i in keys if "Top/" in i]
bkgs = bkgs1 + bkgs2

os.makedirs(args.out_dir, exist_ok=True)

training_variables = [
    "lept1_pt",
    "lept1_eta",
    "pf_met_corr",
    "vbf_jj_m",
    "vbf_jj_Deta",
    "vbf_j1_pt",
    "vbf_j1_eta",
    "vbf_j2_pt",
    "vbf_j2_eta",
    "fatjet_m",
    "fatjet_pt",
    "fatjet_eta",
    "vv_m",
    "vv_pt",
    "vv_eta",
    "boson_centrality",
    "zeppenfeld_w_Deta",
    "zeppenfeld_v_Deta",
    "v_pt",
    "v_eta",
    "ht"
]

weight_variables = [
    "gen_weight"
]

variables_ = open(f"{args.out_dir}/variable_list.txt", "w")
for i in training_variables:
    print(i, file=variables_)
variables_.close()

preselection_code = importlib.import_module(f"selections.{args.region}")
preselection = preselection_code.region_

print(inspect.getsource(preselection))

X_sig = None
w_sig = None

for sig_key in sigs:
    df = dfs[sig_key]["dframe"]
    xs_w = dfs[sig_key]["xs_weight"]

    preselect_df = df[preselection(df, "m") | preselection(df, "e")]

    training_columns = [preselect_df[i] for i in training_variables]

    X_ = np.column_stack(training_columns)
    w_ = xs_w
    for i in weight_variables:
        w_ = w_ * preselect_df[i]

    if X_sig is None:
        X_sig = X_
        w_sig = w_

    else:
        X_sig = np.concatenate([X_sig, X_])
        w_sig = np.concatenate([w_sig, w_])

print("Signal dataset shape: ", X_sig.shape)


X_bkg = None
w_bkg = None

for bkg_key in bkgs:
    df = dfs[bkg_key]["dframe"]
    xs_w = dfs[bkg_key]["xs_weight"]

    preselect_df = df[preselection(df, "m") | preselection(df, "e")]

    training_columns = [preselect_df[i] for i in training_variables]

    X_ = np.column_stack(training_columns)
    w_ = xs_w
    for i in weight_variables:
        w_ = w_ * preselect_df[i]

    if X_bkg is None:
        X_bkg = X_
        w_bkg = w_

    else:
        X_bkg = np.concatenate([X_bkg, X_])
        w_bkg = np.concatenate([w_bkg, w_])

print("Background dataset shape: ", X_bkg.shape)

def make_std_vector(X):
    events = []
    for row in X:
        a = ROOT.std.vector("double")()
        for r in row:
            a.push_back(r)
        events.append(a)
    return events

permuate_sig = np.random.RandomState(seed=42).permutation(X_sig.shape[0])
X_sig = X_sig[permuate_sig]

permuate_bkg = np.random.RandomState(seed=42).permutation(X_bkg.shape[0])
X_bkg = X_bkg[permuate_bkg]

ns_train = int(X_sig.shape[0] * 0.50)
nb_train = int(X_bkg.shape[0] * 0.50)

X_sig_train, w_sig_train = X_sig[:ns_train], w_sig[:ns_train]
X_sig_test, w_sig_test = X_sig[ns_train:], w_sig[ns_train:]

X_bkg_train, w_bkg_train = X_bkg[:nb_train], w_bkg[:nb_train]
X_bkg_test, w_bkg_test = X_bkg[nb_train:], w_bkg[nb_train:]


X_sig_train_vec = make_std_vector(X_sig_train)
X_sig_test_vec = make_std_vector(X_sig_test)

X_bkg_train_vec = make_std_vector(X_bkg_train)
X_bkg_test_vec = make_std_vector(X_bkg_test)


outfile = ROOT.TFile(f"{args.out_dir}/tmva_output.root", "recreate")

(ROOT.TMVA.gConfig().GetVariablePlotting()).fMaxNumOfAllowedVariablesForScatterPlots = 30
(ROOT.TMVA.gConfig().GetVariablePlotting()).fNbinsMVAoutput = 40

factory = ROOT.TMVA.Factory(
    "VBS",
    outfile,
    ":".join([
        "!V", "!Silent",
        "Color", "DrawProgressBar",
        "Transformations=I",
        f"AnalysisType=Classification"
    ])
)

dataloader = ROOT.TMVA.DataLoader(args.out_dir)

for var in training_variables:
    dataloader.AddVariable(var, "F")

for event, w_ in zip(X_sig_train_vec, w_sig_train):
    dataloader.AddSignalTrainingEvent(event, w_)

for event, w_ in zip(X_sig_test_vec, w_sig_test):
    dataloader.AddSignalTestEvent(event, w_)

for event, w_ in zip(X_bkg_train_vec, w_bkg_train):
    dataloader.AddBackgroundTrainingEvent(event, w_)

for event, w_ in zip(X_bkg_test_vec, w_bkg_test):
    dataloader.AddBackgroundTestEvent(event, w_)

dataloader.PrepareTrainingAndTestTree(ROOT.TCut(""), "")

factory.BookMethod(
    dataloader,
    "BDT",
    "BDT",
    ":".join([
        "!H", "!V",
        f"NTrees={args.BDT_NTrees}",
        f"MinNodeSize={args.BDT_MinNodeSize}",
        f"MaxDepth={args.BDT_MaxDepth}",
        f"nCuts={args.BDT_nCuts}",
        f"BoostType=Grad",
        f"Shrinkage={args.BDT_Shrinkage}",
        f"UseBaggedBoost",
        f"BaggedSampleFraction={args.BDT_BaggedFrac}",
        f"NegWeightTreatment=IgnoreNegWeightsInTraining"
    ])
)

factory.TrainAllMethods()
factory.TestAllMethods()
factory.EvaluateAllMethods()
   
outfile.cd()
outfile.Close()

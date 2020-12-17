#!/usr/bin/env python3

import sys
import os
import numpy as np
import ROOT
ROOT.PyConfig.IgnoreCommandLineOptions = True
import argparse

parser = argparse.ArgumentParser()

parser.add_argument("--in-files", dest="in_files", type=str,
                    default="root://cmseos.fnal.gov//store/user/singhr/wv_vbs_ntuples/training_input/z_BDTG3/*.root",
                    help="prepared root files dir, default=%(default)s")

parser.add_argument("--cut", type=str, default="lep2_pt > 0",
                    help="cut to training phase space, default=%(default)s")

parser.add_argument("--boson", type=str, default="W", help="default=%(default)s")

parser.add_argument("--ttree", type=str, default="Events", help="Name of tree, default=%(default)s")

parser.add_argument("--vars", dest="vars", type=str,
                    default="dibos_m,lep2_eta",
                    help="list of variables in tree, default=%(default)s")

parser.add_argument("--weights", dest="weights", type=str,
                    default="xs_weight * genWeight",
                    help="list of weights variables in tree, default=%(default)s")

parser.add_argument("--out-dir", dest="out_dir", type=str, default="BDTG",
                    help="output directory for tmva, default=%(default)s")

parser.add_argument("--grid-search", dest="grid_search", type=int, default=0,
                    help="do grid search on hyper parameters for tmva, default=%(default)s")
parser.add_argument("--grid-search-nTrees", dest="grid_nTrees", action="append", default=[], help="default=%(default)s")
parser.add_argument("--grid-search-minNode", dest="grid_minNode", action="append", default=[], help="default=%(default)s")
parser.add_argument("--grid-search-shrinkage", dest="grid_shrinkage", action="append", default=[], help="default=%(default)s")
parser.add_argument("--grid-search-baggFrac", dest="grid_baggFrac", action="append", default=[], help="default=%(default)s")

parser.add_argument("--BDT-NTrees", dest="BDT_NTrees", type=str, default="100", help="BDT-Config, default=%(default)s")
parser.add_argument("--BDT-MinNodeSize", dest="BDT_MinNodeSize", type=str, default="10", help="BDT-Config, default=%(default)s")
parser.add_argument("--BDT-MaxDepth", dest="BDT_MaxDepth", type=str, default="3", help="BDT-Config, default=%(default)s")
parser.add_argument("--BDT-nCuts", dest="BDT_nCuts", type=str, default="100", help="BDT-Config, default=%(default)s")
parser.add_argument("--BDT-Shrinkage", dest="BDT_Shrinkage", type=str, default="0.05", help="BDT-Config, default=%(default)s")
parser.add_argument("--BDT-BaggedFrac", dest="BDT_BaggedFrac", type=str, default="0.5", help="BDT-Config, default=%(default)s")

args = parser.parse_args()

print("Args")
print("==================")
print(args)

df = ROOT.RDataFrame("Events", f"{args.in_files}")

os.makedirs(args.out_dir, exist_ok=True)

training_variables = "".join(args.vars.split()).split(",")
training_region = args.cut
training_weight = args.weights

print("Training vars ... ")
print("==================")
print(training_variables)
print("==================")

print("Training region ... ")
print("====================")
print(" ".join(training_region.split()))
print("====================")


variables_ = open(f"{args.out_dir}/variable_list.txt", "w")
for i in training_variables:
    print(i, file=variables_)
variables_.close()

df_training_region = df.Filter(training_region).Define("training_weight", training_weight)

columns = training_variables + ["training_weight"]

if args.boson == "W":
    df_training_sig_ = df_training_region.Filter("sample_tag == \"VBS_EWK\"")
    df_training_bkg_ = df_training_region.Filter("sample_tag == \"WJets_HT\" || sample_tag == \"Top\"")

if args.boson == "Z":
    df_training_sig_ = df_training_region.Filter("sample_tag == \"VBS_EWK\"")
    df_training_bkg_ = df_training_region.Filter("sample_tag == \"DYJets_HT\"")

df_training_sig = df_training_sig_.AsNumpy(columns=columns)
df_training_bkg = df_training_bkg_.AsNumpy(columns=columns)

X_sig = np.column_stack([df_training_sig[i] for i in training_variables])
w_sig = df_training_sig["training_weight"]

X_bkg = np.column_stack([df_training_bkg[i] for i in training_variables])
w_bkg = df_training_bkg["training_weight"]


print("Signal dataset shape: ", X_sig.shape)
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
        f"MinNodeSize={args.BDT_MinNodeSize}%",
        f"MaxDepth={args.BDT_MaxDepth}",
        f"nCuts={args.BDT_nCuts}",
        f"BoostType=Grad",
        f"Shrinkage={args.BDT_Shrinkage}",
        f"UseBaggedBoost",
        f"BaggedSampleFraction={args.BDT_BaggedFrac}",
        f"NegWeightTreatment=IgnoreNegWeightsInTraining"
    ])
)

if args.grid_search != 0:
    for nTrees in args.grid_nTrees:
        for minNode in args.grid_minNode:
            for shrinkage in args.grid_shrinkage:
                for baggFrac in args.grid_baggFrac:
                    factory.BookMethod(
                        dataloader,"BDT",
                        f"BDT_nTrees_{nTrees}_minNode_{minNode}_shrinkage_{shrinkage}_baggFrac_{baggFrac}",
                        ":".join(["!H", "!V",
                                  f"NTrees={nTrees}",f"MinNodeSize={minNode}%",
                                  f"MaxDepth=3",f"nCuts=100",f"BoostType=Grad",
                                  f"Shrinkage={shrinkage}",f"UseBaggedBoost",
                                  f"BaggedSampleFraction={baggFrac}",
                                  f"NegWeightTreatment=IgnoreNegWeightsInTraining"])
                    )

factory.TrainAllMethods()
factory.TestAllMethods()
factory.EvaluateAllMethods()
   
outfile.cd()
outfile.Close()

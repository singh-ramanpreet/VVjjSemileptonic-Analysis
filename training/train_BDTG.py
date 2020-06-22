#!/usr/bin/env python3

import sys
import os
import numpy as np
import ROOT
ROOT.PyConfig.IgnoreCommandLineOptions = True
import argparse

parser = argparse.ArgumentParser()

parser.add_argument("--in-dir", dest="in_dir", type=str, default="2018_Jun4",
                    help="prepared root files dir relative to /store/user/singhr/, default=%(default)s")
parser.add_argument("--boson", type=str, default="W", help="default=%(default)s")
parser.add_argument("--var-set", dest="var_set", type=str, default="wv",
                    help="variable set wv or wjj, default=%(default)s")
parser.add_argument("--out-dir", dest="out_dir", type=str, default="BDTG",
                    help="output directory for tmva, default=%(default)s")
parser.add_argument("--BDT-NTrees", dest="BDT_NTrees", type=str, default="100", help="BDT-Config, default=%(default)s")
parser.add_argument("--BDT-MinNodeSize", dest="BDT_MinNodeSize", type=str, default="10%", help="BDT-Config, default=%(default)s")
parser.add_argument("--BDT-MaxDepth", dest="BDT_MaxDepth", type=str, default="3", help="BDT-Config, default=%(default)s")
parser.add_argument("--BDT-nCuts", dest="BDT_nCuts", type=str, default="100", help="BDT-Config, default=%(default)s")
parser.add_argument("--BDT-Shrinkage", dest="BDT_Shrinkage", type=str, default="0.05", help="BDT-Config, default=%(default)s")
parser.add_argument("--BDT-BaggedFrac", dest="BDT_BaggedFrac", type=str, default="0.5", help="BDT-Config, default=%(default)s")

args = parser.parse_args()

print(args)

df = ROOT.RDataFrame("Events", f"root://cmseos.fnal.gov//store/user/singhr/{args.in_dir}/*.root")

preselect_z_e = "lept_channel == 1 && fabs(lept1_eta) < 2.5 && !(fabs(lept1_eta) > 1.4442 && fabs(lept1_eta) < 1.566)" \
                " && fabs(lept2_eta) < 2.5 && !(fabs(lept2_eta) > 1.4442 && fabs(lept2_eta) < 1.566)" \
                " && lept1_pt > 40"

preselect_z_m = "lept_channel == 0 && fabs(lept1_eta) < 2.4" \
                " && fabs(lept2_eta) < 2.4" \
                " && lept1_pt > 35"

preselect_z_sr = "lept2_pt > 20" \
                 " && lept1_q * lept2_q < 0" \
                 " && v_m > 75 && v_m < 105" \
                 " && vbf_jj_m > 500" \
                 " && vbf_j1_pt > 50" \
                 " && vbf_j2_pt > 50" \
                 " && vbf_jj_Deta > 2.5"

preselect_zv = preselect_z_sr  + " && fatjet_pt > 200 && fabs(fatjet_eta) < 2.4" \
                                 " && fatjet_tau21 < 0.55" \
                                 " && fatjet_m > 65 && fatjet_m < 105"

preselect_zjj = preselect_z_sr + " && dijet_pt > 0" \
                                 " && dijet_j2_pt > 30 && dijet_j1_pt > 30" \
                                 " && dijet_m > 65 && dijet_m < 105"

training_region_zv = preselect_zv + " && ((" + preselect_z_e + ") || (" + preselect_z_m + "))"
training_region_zjj = preselect_zjj + " && ((" + preselect_z_e + ") || (" + preselect_z_m + "))"


os.makedirs(args.out_dir, exist_ok=True)

training_variables_wv = [
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

training_variables_wjj = [
    "lept1_pt",
    "lept1_eta",
    "pf_met_corr",
    "vbf_jj_m",
    "vbf_jj_Deta",
    "vbf_j1_pt",
    "vbf_j1_eta",
    "vbf_j2_pt",
    "vbf_j2_eta",
    "dijet_m",
    "dijet_pt",
    "dijet_eta",
    "vv_m",
    "vv_pt",
    "vv_eta",
    "boson_centrality",
    "zeppenfeld_w_Deta",
    "zeppenfeld_v_Deta",
    "v_pt",
    "v_eta",
    "ht_resolved"
]

training_variables_zv = [
    #"lept1_pt",
    #"lept1_eta",
    #"lept2_pt",
    #"lept2_eta",
    "vbf_jj_m",
    #"vbf_jj_Deta",
    #"vbf_j1_pt",
    #"vbf_j1_eta",
    #"vbf_j2_pt",
    #"vbf_j2_eta",
    #"fatjet_m",
    #"fatjet_pt",
    #"fatjet_eta",
    "vv_m",
    #"vv_pt",
    #"vv_eta",
    #"boson_centrality",
    "zeppenfeld_w_Deta",
    #"zeppenfeld_v_Deta",
    #"v_pt",
    #"v_eta",
    #"ht"
]

training_variables_zjj = [
    #"lept1_pt",
    #"lept1_eta",
    #"lept2_pt",
    "lept2_eta",
    "vbf_jj_m",
    #"vbf_jj_Deta",
    #"vbf_j1_pt",
    #"vbf_j1_eta",
    #"vbf_j2_pt",
    #"vbf_j2_eta",
    #"dijet_m",
    #"dijet_pt",
    #"dijet_eta",
    "vv_m",
    #"vv_pt",
    #"vv_eta",
    #"boson_centrality",
    "zeppenfeld_w_Deta",
    #"zeppenfeld_v_Deta",
    #"v_pt",
    #"v_eta",
    "ht_resolved"
]

if args.var_set == "wv":
    training_variables = training_variables_wv

elif args.var_set == "wjj":
    training_variables = training_variables_wjj

elif args.var_set == "zv":
    training_variables = training_variables_zv
    training_region = training_region_zv

elif args.var_set == "zjj":
    training_variables = training_variables_zjj
    training_region = training_region_zjj

else:
    print("select training variable set")

print(training_variables)
print(training_region)

variables_ = open(f"{args.out_dir}/variable_list.txt", "w")
for i in training_variables:
    print(i, file=variables_)
variables_.close()


df_training_region = df.Filter(training_region).Define("training_weight", "xs_weight")

columns = training_variables + ["training_weight"]

if args.boson == "Z":
    df_training_sig_ = df_training_region.Filter("sample_tag == \"VBS_EWK\"")
    df_training_bkg_ = df_training_region.Filter("sample_tag == \"DYJets_LO\"")

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

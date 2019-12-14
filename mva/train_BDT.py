#!/usr/bin/env python3

import ROOT
import json
import os

dataloader_name = "BDT_1"
os.makedirs(dataloader_name, exist_ok=True)

output_file = ROOT.TFile(f"{dataloader_name}/training_output.root", "recreate")

factory = ROOT.TMVA.Factory(
    "VBS",
    output_file,
    ":".join([
        "!V", "!Silent",
        "Color", "DrawProgressBar",
        "Transformations=I",
        "AnalysisType=Classification"
    ])
)

dataloader = ROOT.TMVA.DataLoader(dataloader_name)

samples_dict = json.load(open("../datasets_2016.json", "r"))

input_trees = []

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

        root_file = ROOT.TFile.Open(root_file)

        if key == "VBS_EWK":
            input_trees.append((root_file, xs_weight, "Signal"))

        elif "data" in key:
            continue

        else:
            input_trees.append((root_file, xs_weight, "Background"))

for i_tree, treeWeight, treeClass in input_trees:
    dataloader.AddTree(i_tree.Get("otree"), treeClass, treeWeight)

# leptons
dataloader.AddVariable("l_pt1", "F")
dataloader.AddVariable("l_eta1", "F")
dataloader.AddVariable("pfMET_Corr", "F")

# tagged jets
dataloader.AddVariable("njets", "F")
dataloader.AddVariable("vbf_maxpt_jj_m", "F")
dataloader.AddVariable("vbf_maxpt_jj_Deta", "F")
dataloader.AddVariable("vbf_maxpt_j1_pt", "F")
dataloader.AddVariable("vbf_maxpt_j2_pt", "F")
dataloader.AddVariable("vbf_maxpt_j1_eta", "F")
dataloader.AddVariable("vbf_maxpt_j2_eta", "F")

# AK8 jet
dataloader.AddVariable("PuppiAK8_jet_mass_so_corr", "F")
dataloader.AddVariable("ungroomed_PuppiAK8_jet_pt", "F")
dataloader.AddVariable("ungroomed_PuppiAK8_jet_eta", "F")
#dataloader.AddVariable("PuppiAK8_jet_tau2tau1", "F")

# WV system
dataloader.AddVariable("mass_lvj_type0_PuppiAK8", "F")
dataloader.AddVariable("pt_lvj_type0_PuppiAK8", "F")
dataloader.AddVariable("eta_lvj_type0_PuppiAK8", "F")
#dataloader.AddVariable("deltaphi_METak8jet", "F")

dataloader.AddVariable("BosonCentrality_type0", "F")
dataloader.AddVariable("ZeppenfeldWH_dEtajj := ZeppenfeldWH/vbf_maxpt_jj_Deta", "F")
dataloader.AddVariable("ZeppenfeldWL_dEtajj := ZeppenfeldWL_type0/vbf_maxpt_jj_Deta", "F")

# angles
dataloader.AddVariable("costheta1_type0", "F")
dataloader.AddVariable("costheta2_type0", "F")
dataloader.AddVariable("phi_type0", "F")
dataloader.AddVariable("phi1_type0", "F")
dataloader.AddVariable("costhetastar_type0", "F")

# Leptonic W = lep + nu
dataloader.AddVariable("v_pt_type0", "F")
dataloader.AddVariable("v_eta_type0", "F")
dataloader.AddVariable("v_mt_type0", "F")

# HT
dataloader.AddVariable("ht := ungroomed_PuppiAK8_jet_pt+vbf_maxpt_j1_pt+vbf_maxpt_j2_pt", "F")

# gen weights
dataloader.SetSignalWeightExpression("genWeight")
dataloader.SetBackgroundWeightExpression("genWeight")

preselection = """
(type==1 || type==0) 
&& (l_pt2<0)
&& (l_pt1>30)
&& (pfMET_Corr>50)
&& (nBTagJet_loose==0)
&& (vbf_maxpt_j1_pt>30)
&& (vbf_maxpt_j2_pt>30) 
&& (vbf_maxpt_jj_m>500)
&& (vbf_maxpt_jj_Deta>2.5)
&& (
    (ungroomed_PuppiAK8_jet_pt>200)
    && (abs(ungroomed_PuppiAK8_jet_eta)<2.4)
    )
&& (
    (PuppiAK8_jet_mass_so_corr>40)
    && (PuppiAK8_jet_mass_so_corr<150)
    )
&& (PuppiAK8_jet_tau2tau1<0.55)
&& (
    (ZeppenfeldWL_type0/vbf_maxpt_jj_Deta>-1.0)
    && (ZeppenfeldWL_type0/vbf_maxpt_jj_Deta<1.0)
    )
&& (
    (ZeppenfeldWH/vbf_maxpt_jj_Deta>-1.0)
    && (ZeppenfeldWH/vbf_maxpt_jj_Deta<1.0)
    )
&& (phi_type0>-999.0)
"""

preselection = preselection.replace("\n", " ")

N = 1000
dataloader.PrepareTrainingAndTestTree(
    ROOT.TCut(preselection),
    ":".join([
        "!V",
        "SplitMode=Random",
        "NormMode=NumEvents",
        f"nTrain_Signal={N}",
        f"nTest_Signal={N}",
        f"nTrain_Background={N}",
        f"nTest_Background={N}"
    ])
)

factory.BookMethod(
    dataloader,
    ROOT.TMVA.Types.kBDT,
    "BDTG",
    ":".join([
        "!H", "!V", 
        "NTrees=1000",
        "MinNodeSize=2.5%", 
        "BoostType=Grad",
        "Shrinkage=0.10",
        "UseBaggedBoost", "BaggedSampleFraction=0.5", 
        "NegWeightTreatment=Pray"
    ])
)

factory.TrainAllMethods()
factory.TestAllMethods()
factory.EvaluateAllMethods()
   
output_file.cd()
output_file.Close()

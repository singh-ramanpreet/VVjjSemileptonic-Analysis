#!/usr/bin/env python3

import sys
import os
import json
import numpy as np
import ROOT
import awkward
import uproot
import argparse

parser = argparse.ArgumentParser()

parser.add_argument(
    "--datasets", type=str, default="datasets_2016.json",
    help="json file containing info of datasets, default=%(default)s"
    )

parser.add_argument(
    "--channel", type=str, default="mu",
    help="muon or electron channel, default=%(default)s"
    )

parser.add_argument(
    "--boson", type=str, default="W",
    help="W or Z, default=%(default)s"
    )

parser.add_argument(
    "--region", type=str, default="signal_loose",
    help="region , default=%(default)s"
    )

args = parser.parse_args()

# samples dict
# ============
samples_dict = json.load(open(args.datasets, "r"))

# a class to book multiple hists
# ==============================
class book_hist_dict:
    def __init__(self, xbins, xlow=0, xup=1, titleX="", units="", name="", 
                 keys=[], keys_sub=[]):
        self.xbins = xbins
        self.xlow = xlow
        self.xup = xup
        self.titleX = titleX
        self.units = units
        self.name = name
        self.keys = keys
        self.keys_sub = keys_sub
    
    def hist_1D(self):
        if type(self.xbins) == int:
            variable = ROOT.TH1F("", "", self.xbins, self.xlow, self.xup)
            bw = variable.GetBinWidth(1)
        
        elif type(self.xbins) == np.ndarray:
            variable = ROOT.TH1F("", "", len(self.xbins) - 1, self.xbins.astype(np.float64))
            bw = None
        
        else:
            return None

        titleX = self.titleX
        if bw is not None:
            titleY = "Events/%s" % bw
        else:
            titleY = "Events"
        
        if self.units != "":
            titleX = self.titleX + "(" + self.units + ")"
            titleY = titleY + " " + self.units
        
        variable.SetTitle("%s;%s;%s" % (titleX, titleX, titleY))
        
        if self.name != "":
            variable.SetName(self.name)
        else:
            variable.SetName(self.titleX)
        
        return variable
    
    def clone(self):
        hist_dict = {}
        
        for key in self.keys:
            name_ = key + "_" + self.hist_1D().GetName()
            hist_dict[key] = self.hist_1D().Clone()
            hist_dict[key].SetName(name_)

            for key_sub in self.keys_sub:
                name = name_ + "_" + key_sub
                hist_dict[key + "_" + key_sub] = self.hist_1D().Clone()
                hist_dict[key + "_" + key_sub].SetName(name)
                
        return hist_dict

# book histograms
# ===============
hist_keys = list(samples_dict.keys())

h_lept_pt1 = book_hist_dict(30, 0, 300, titleX="lept_pt1", units="GeV", keys=hist_keys).clone()
h_lept_pt2 = book_hist_dict(30, 0, 300, titleX="lept_pt2", units="GeV", keys=hist_keys).clone()

h_lept_eta1 = book_hist_dict(25, -2.5, 2.5, titleX="lept_eta1", keys=hist_keys).clone()
h_lept_eta2 = book_hist_dict(25, -2.5, 2.5, titleX="lept_eta2", keys=hist_keys).clone()

h_lept_phi1 = book_hist_dict(32, -3.2, 3.2, titleX="lept_phi1", keys=hist_keys).clone()
h_lept_phi2 = book_hist_dict(32, -3.2, 3.2, titleX="lept_phi2", keys=hist_keys).clone()

h_mass_WV = book_hist_dict(50, 0, 2500, titleX="mass_WV", units="GeV", keys=hist_keys).clone()
h_mass_ZV = book_hist_dict(50, 0, 2500, titleX="mass_ZV", units="GeV", keys=hist_keys).clone()

h_PuppiAK8jet_e2_sdb1 = book_hist_dict(80, 0.0, 0.4, titleX="PuppiAK8jet_e2_sdb1", keys=hist_keys).clone()
h_PuppiAK8jet_e3_sdb1 = book_hist_dict(100, 0.0, 0.05, titleX="PuppiAK8jet_e3_sdb1", keys=hist_keys).clone()
h_PuppiAK8jet_e3_v1_sdb1 = book_hist_dict(120, 0.0, 0.06, titleX="PuppiAK8jet_e3_v1_sdb1", keys=hist_keys).clone()
h_PuppiAK8jet_e3_v2_sdb1 = book_hist_dict(100, 0.0, 0.05, titleX="PuppiAK8jet_e3_v2_sdb1", keys=hist_keys).clone()

h_PuppiAK8jet_e2_sdb2 = book_hist_dict(60, 0.0, 0.3, titleX="PuppiAK8jet_e2_sdb2", keys=hist_keys).clone()
h_PuppiAK8jet_e3_sdb2 = book_hist_dict(80, 0.0, 0.04, titleX="PuppiAK8jet_e3_sdb2", keys=hist_keys).clone()
h_PuppiAK8jet_e3_v1_sdb2 = book_hist_dict(60, 0.0, 0.03, titleX="PuppiAK8jet_e3_v1_sdb2", keys=hist_keys).clone()
h_PuppiAK8jet_e3_v2_sdb2 = book_hist_dict(60, 0.0, 0.03, titleX="PuppiAK8jet_e3_v2_sdb2", keys=hist_keys).clone()

h_PuppiAK8jet_e4_v1_sdb1 = book_hist_dict(160, 0.0, 0.008, titleX="PuppiAK8jet_e4_v1_sdb1", keys=hist_keys).clone()
h_PuppiAK8jet_e4_v2_sdb1 = book_hist_dict(80, 0.0, 0.004, titleX="PuppiAK8jet_e4_v2_sdb1", keys=hist_keys).clone()
h_PuppiAK8jet_e4_v1_sdb2 = book_hist_dict(40, 0.0, 0.002, titleX="PuppiAK8jet_e4_v1_sdb2", keys=hist_keys).clone()
h_PuppiAK8jet_e4_v2_sdb2 = book_hist_dict(40, 0.0, 0.0004, titleX="PuppiAK8jet_e4_v2_sdb2", keys=hist_keys).clone()

h_PuppiAK8jet_n2_sdb1 = book_hist_dict(100, 0.0, 0.5, titleX="PuppiAK8jet_n2_sdb1", keys=hist_keys).clone()
h_PuppiAK8jet_n2_sdb2 = book_hist_dict(80, 0.0, 0.4, titleX="PuppiAK8jet_n2_sdb2", keys=hist_keys).clone()

h_PuppiAK8jet_d2_sdb1 = book_hist_dict(80, 0.0, 4.0, titleX="PuppiAK8jet_d2_sdb1", keys=hist_keys).clone()
h_PuppiAK8jet_d2_sdb2 = book_hist_dict(140, 0.0, 7.0, titleX="PuppiAK8jet_d2_sdb2", keys=hist_keys).clone()

h_PuppiAK8jet_tau2tau1 = book_hist_dict(100, 0.0, 1.0, titleX="PuppiAK8jet_tau2tau1", keys=hist_keys).clone()

h2 = ROOT.TH2F("n2_sdb1_tau2tau1", ";n2_sdb1;tau2tau1", 100, 0.0, 0.5, 100, 0.0, 1.0)
h2_n2_sdb1_tau2tau1 = {key: h2.Clone(f"{key}_{h2.GetName()}") for key in hist_keys}

h2 = ROOT.TH2F("n2_sdb2_tau2tau1", ";n2_sdb2;tau2tau1", 80, 0.0, 0.4, 100, 0.0, 1.0)
h2_n2_sdb2_tau2tau1 = {key: h2.Clone(f"{key}_{h2.GetName()}") for key in hist_keys}

h2 = ROOT.TH2F("e2_sdb1_e3_sdb1", ";e2_sdb1;e3_sdb1", 80, 0.0, 0.4, 100, 0.0, 0.05)
h2_e2_sdb1_e3_sdb1 = {key: h2.Clone(f"{key}_{h2.GetName()}") for key in hist_keys}

h2 = ROOT.TH2F("e2_sdb1_e3_v1_sdb1", ";e2_sdb1;e3_v1_sdb1", 40, 0.0, 0.4, 120, 0.0, 0.06)
h2_e2_sdb1_e3_v1_sdb1 = {key: h2.Clone(f"{key}_{h2.GetName()}") for key in hist_keys}




# fill ROOT histogram with numpy array
# ===================================
def fill_hist_array(hist, array, weight=1.0):

    if len(array) == 0:
        return None

    if type(weight) == float:
        for v in array:
            hist.Fill(v, weight)

    else:
        for v, w in zip(array, weight):
            hist.Fill(v, w)

    return None

# loop over samples, apply selections,
# and fill histograms.
# ===================================
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

        df = uproot.lazyarrays(root_file, "otree")

        if "isResolved" not in df.columns:
            df["isResolved"] = False

        # common veto
        veto = ( 
            (df["nBTagJet_loose"] == 0) &
            (df["vbf_maxpt_j1_pt"] > 30) &
            (df["vbf_maxpt_j2_pt"] > 30)
        )

        # W channel
        W_channel = (
            (df["l_pt1"] > 50) &
            (df["l_pt2"] < 0)
        )

        # Z channel
        Z_channel = (
            (df["l_pt1"] > 50) &
            (df["l_pt2"] > 30) &
            (df["dilep_m"] > (91.1876 - 7.5)) &
            (df["dilep_m"] < (91.1876 + 7.5))
        )

        # e channel
        e_channel = (
            (df["type"] == 1) &
            (np.abs(df["l_eta1"]) < 2.5) &
            ~(
                (np.abs(df["l_eta1"]) > 1.4442) &
                (np.abs(df["l_eta1"]) < 1.566)
            )
        )

        e_channel2 = (
            (np.abs(df["l_eta2"]) < 2.5) &
            ~(
                (np.abs(df["l_eta2"]) > 1.4442) &
                (np.abs(df["l_eta2"]) < 1.566)
            )
        )

        # mu channel
        mu_channel = (
            (df["type"] == 0) &
            (np.abs(df["l_eta1"]) < 2.4)
        )

        mu_channel2 = (np.abs(df["l_eta2"]) < 2.4)

        signal_region_loose = (
            (df["isResolved"] == False) &
            (df["ungroomed_PuppiAK8_jet_pt"] > 200 ) &
            (np.abs(df["ungroomed_PuppiAK8_jet_eta"]) < 2.4 ) &
            #(df["PuppiAK8_jet_tau2tau1"] < 0.55) &
            (df["PuppiAK8_jet_mass_so_corr"] > 65) &
            (df["PuppiAK8_jet_mass_so_corr"] < 105) &
            (df["vbf_maxpt_jj_m"] > 300) &
            (np.abs(df["vbf_maxpt_j2_eta"] - df["vbf_maxpt_j1_eta"]) > 2.0)
        )

        signal_region_tight = (
            (df["isResolved"] == False) &
            (df["ungroomed_PuppiAK8_jet_pt"] > 200 ) &
            (np.abs(df["ungroomed_PuppiAK8_jet_eta"]) < 2.4 ) &
            #(df["PuppiAK8_jet_tau2tau1"] < 0.55) &
            (df["PuppiAK8_jet_mass_so_corr"] > 65) &
            (df["PuppiAK8_jet_mass_so_corr"] < 105) &
            (df["vbf_maxpt_jj_m"] > 800) &
            (np.abs(df["vbf_maxpt_j2_eta"] - df["vbf_maxpt_j1_eta"]) > 4.0)
        )

        additional_W_cuts = (
            (df["BosonCentrality_type0"] > 1.0) &
            (np.abs(df["ZeppenfeldWL_type0"])/(np.abs(df["vbf_maxpt_j2_eta"] - df["vbf_maxpt_j1_eta"])) < 0.3) &
            (np.abs(df["ZeppenfeldWH"])/(np.abs(df["vbf_maxpt_j2_eta"] - df["vbf_maxpt_j1_eta"])) < 0.3)
        )

        if args.boson == "W":

            boson_channel_sel = W_channel

            if args.channel == "mu":

                lep_channel_sel = mu_channel & (df["pfMET_Corr"] > 50)

            if args.channel == "e":

                lep_channel_sel = e_channel & (df["pfMET_Corr"] > 80)


        if args.boson == "Z":

            boson_channel_sel = Z_channel

            if args.channel == "mu":

                lep_channel_sel = mu_channel & mu_channel2

            if args.channel == "e":

                lep_channel_sel = e_channel & e_channel2


        if args.region == "signal_loose":

            region_sel = signal_region_loose

        if args.region == "signal_tight":

            region_sel = signal_region_tight

            if args.boson == "W":

                region_sel = signal_region_tight & additional_W_cuts

        skim_df = df[veto & lep_channel_sel & boson_channel_sel & region_sel]

        if args.boson == "W":
            total_weight = xs_weight * skim_df["genWeight"] * skim_df["trig_eff_Weight"] \
                            * skim_df["id_eff_Weight"] * skim_df["pu_Weight"] * skim_df["btag0Wgt"]

        if args.boson == "Z":
            total_weight = xs_weight * skim_df["genWeight"] * skim_df["trig_eff_Weight"] * skim_df["trig_eff_Weight2"] \
                            * skim_df["id_eff_Weight"] * skim_df["id_eff_Weight2"] * skim_df["pu_Weight"] * skim_df["btag0Wgt"]

        print("filling hists .... ")

        lept_pt1 = skim_df["l_pt1"]
        fill_hist_array(h_lept_pt1[key], lept_pt1, total_weight)

        lept_pt2 = skim_df["l_pt2"]
        fill_hist_array(h_lept_pt2[key], lept_pt2, total_weight)

        lept_eta1 = skim_df["l_eta1"]
        fill_hist_array(h_lept_eta1[key], lept_eta1, total_weight)

        lept_eta2 = skim_df["l_eta2"]
        fill_hist_array(h_lept_eta2[key], lept_eta2, total_weight)

        lept_phi1 = skim_df["l_phi1"]
        fill_hist_array(h_lept_phi1[key], lept_phi1, total_weight)

        lept_phi2 = skim_df["l_phi2"]
        fill_hist_array(h_lept_phi2[key], lept_phi2, total_weight)

        mass_WV = skim_df["mass_lvj_type0_PuppiAK8"]
        fill_hist_array(h_mass_WV[key], mass_WV, total_weight)

        mass_ZV = skim_df["mass_llj_PuppiAK8"]
        fill_hist_array(h_mass_ZV[key], mass_ZV, total_weight)

        PuppiAK8jet_e2_sdb1 = skim_df["PuppiAK8jet_e2_sdb1"]
        fill_hist_array(h_PuppiAK8jet_e2_sdb1[key], PuppiAK8jet_e2_sdb1, total_weight)

        PuppiAK8jet_e3_sdb1 = skim_df["PuppiAK8jet_e3_sdb1"]
        fill_hist_array(h_PuppiAK8jet_e3_sdb1[key], PuppiAK8jet_e3_sdb1, total_weight)

        PuppiAK8jet_e3_v1_sdb1 = skim_df["PuppiAK8jet_e3_v1_sdb1"]
        fill_hist_array(h_PuppiAK8jet_e3_v1_sdb1[key], PuppiAK8jet_e3_v1_sdb1, total_weight)

        PuppiAK8jet_e3_v2_sdb1 = skim_df["PuppiAK8jet_e3_v2_sdb1"]
        fill_hist_array(h_PuppiAK8jet_e3_v2_sdb1[key], PuppiAK8jet_e3_v2_sdb1, total_weight)

        PuppiAK8jet_e2_sdb2 = skim_df["PuppiAK8jet_e2_sdb2"]
        fill_hist_array(h_PuppiAK8jet_e2_sdb2[key], PuppiAK8jet_e2_sdb2, total_weight)

        PuppiAK8jet_e3_sdb2 = skim_df["PuppiAK8jet_e3_sdb2"]
        fill_hist_array(h_PuppiAK8jet_e3_sdb2[key], PuppiAK8jet_e3_sdb2, total_weight)

        PuppiAK8jet_e3_v1_sdb2 = skim_df["PuppiAK8jet_e3_v1_sdb2"]
        fill_hist_array(h_PuppiAK8jet_e3_v1_sdb2[key], PuppiAK8jet_e3_v1_sdb2, total_weight)

        PuppiAK8jet_e3_v2_sdb2 = skim_df["PuppiAK8jet_e3_v2_sdb2"]
        fill_hist_array(h_PuppiAK8jet_e3_v2_sdb2[key], PuppiAK8jet_e3_v2_sdb2, total_weight)

        PuppiAK8jet_e4_v1_sdb1 = skim_df["PuppiAK8jet_e4_v1_sdb1"]
        fill_hist_array(h_PuppiAK8jet_e4_v1_sdb1[key], PuppiAK8jet_e4_v1_sdb1, total_weight)

        PuppiAK8jet_e4_v2_sdb1 = skim_df["PuppiAK8jet_e4_v2_sdb1"]
        fill_hist_array(h_PuppiAK8jet_e4_v2_sdb1[key], PuppiAK8jet_e4_v2_sdb1, total_weight)

        PuppiAK8jet_e4_v1_sdb2 = skim_df["PuppiAK8jet_e4_v1_sdb2"]
        fill_hist_array(h_PuppiAK8jet_e4_v1_sdb2[key], PuppiAK8jet_e4_v1_sdb2, total_weight)

        PuppiAK8jet_e4_v2_sdb2 = skim_df["PuppiAK8jet_e4_v2_sdb2"]
        fill_hist_array(h_PuppiAK8jet_e4_v2_sdb2[key], PuppiAK8jet_e4_v2_sdb2, total_weight)

        PuppiAK8jet_n2_sdb1 = PuppiAK8jet_e3_v2_sdb1 / (PuppiAK8jet_e2_sdb1)**2
        fill_hist_array(h_PuppiAK8jet_n2_sdb1[key], PuppiAK8jet_n2_sdb1, total_weight)

        PuppiAK8jet_n2_sdb2 = PuppiAK8jet_e3_v2_sdb2 / (PuppiAK8jet_e2_sdb2)**2
        fill_hist_array(h_PuppiAK8jet_n2_sdb2[key], PuppiAK8jet_n2_sdb2, total_weight)

        PuppiAK8jet_d2_sdb1 = PuppiAK8jet_e3_sdb1 / (PuppiAK8jet_e2_sdb1)**3
        fill_hist_array(h_PuppiAK8jet_d2_sdb1[key], PuppiAK8jet_d2_sdb1, total_weight)

        PuppiAK8jet_d2_sdb2 = PuppiAK8jet_e3_sdb2 / (PuppiAK8jet_e2_sdb2)**3
        fill_hist_array(h_PuppiAK8jet_d2_sdb2[key], PuppiAK8jet_d2_sdb2, total_weight)

        PuppiAK8jet_tau2tau1 = skim_df["PuppiAK8_jet_tau2tau1"]
        fill_hist_array(h_PuppiAK8jet_tau2tau1[key], PuppiAK8jet_tau2tau1, total_weight)

        if len(PuppiAK8jet_n2_sdb1) != 0:
            h2_n2_sdb1_tau2tau1[key].FillN(len(PuppiAK8jet_n2_sdb1),
                                           np.array(PuppiAK8jet_n2_sdb1, np.float64),
                                           np.array(PuppiAK8jet_tau2tau1, np.float64),
                                           np.array(total_weight, np.float64))

        if len(PuppiAK8jet_n2_sdb2) != 0:
            h2_n2_sdb2_tau2tau1[key].FillN(len(PuppiAK8jet_n2_sdb2),
                                       np.array(PuppiAK8jet_n2_sdb2, np.float64),
                                       np.array(PuppiAK8jet_tau2tau1, np.float64),
                                       np.array(total_weight, np.float64))
        if len(PuppiAK8jet_e2_sdb1) != 0:
            h2_e2_sdb1_e3_sdb1[key].FillN(len(PuppiAK8jet_e2_sdb1),
                                      np.array(PuppiAK8jet_e2_sdb1, np.float64),
                                      np.array(PuppiAK8jet_e3_sdb1, np.float64),
                                      np.array(total_weight, np.float64))
        if len(PuppiAK8jet_e2_sdb1) != 0:
            h2_e2_sdb1_e3_v1_sdb1[key].FillN(len(PuppiAK8jet_e2_sdb1),
                                         np.array(PuppiAK8jet_e2_sdb1, np.float64),
                                         np.array(PuppiAK8jet_e3_v1_sdb1, np.float64),
                                         np.array(total_weight, np.float64))

# write hists to root file
# ========================
out_hist_file = ROOT.TFile(f"{args.region}_{args.boson}_{args.channel}.root", "RECREATE")
out_hist_file.cd()

for k in samples_dict:
    h_lept_pt1[k].Write()
    h_lept_pt2[k].Write()
    h_lept_eta1[k].Write()
    h_lept_eta2[k].Write()
    h_lept_phi1[k].Write()
    h_lept_phi2[k].Write()
    h_mass_WV[k].Write()
    h_mass_ZV[k].Write()

    h_PuppiAK8jet_e2_sdb1[k].Write()
    h_PuppiAK8jet_e3_sdb1[k].Write()
    h_PuppiAK8jet_e3_v1_sdb1[k].Write()
    h_PuppiAK8jet_e3_v2_sdb1[k].Write()
    h_PuppiAK8jet_e2_sdb2[k].Write()
    h_PuppiAK8jet_e3_sdb2[k].Write()
    h_PuppiAK8jet_e3_v1_sdb2[k].Write()
    h_PuppiAK8jet_e3_v2_sdb2[k].Write()
    h_PuppiAK8jet_e4_v1_sdb1[k].Write()
    h_PuppiAK8jet_e4_v2_sdb1[k].Write()
    h_PuppiAK8jet_e4_v1_sdb2[k].Write()
    h_PuppiAK8jet_e4_v2_sdb2[k].Write()
    h_PuppiAK8jet_n2_sdb1[k].Write()
    h_PuppiAK8jet_n2_sdb2[k].Write()
    h_PuppiAK8jet_d2_sdb1[k].Write()
    h_PuppiAK8jet_d2_sdb2[k].Write()
    h_PuppiAK8jet_tau2tau1[k].Write()
    h2_n2_sdb1_tau2tau1[k].Write()
    h2_n2_sdb2_tau2tau1[k].Write()
    h2_e2_sdb1_e3_sdb1[k].Write()
    h2_e2_sdb1_e3_v1_sdb1[k].Write()

out_hist_file.Write()
out_hist_file.Close()

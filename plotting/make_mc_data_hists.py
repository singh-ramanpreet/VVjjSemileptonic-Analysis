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

h_lept_eta1 = book_hist_dict(25, -2.5, 2.5, titleX="lept_eta1", units="GeV", keys=hist_keys).clone()
h_lept_eta2 = book_hist_dict(25, -2.5, 2.5, titleX="lept_eta2", units="GeV", keys=hist_keys).clone()

h_lept_phi1 = book_hist_dict(32, -3.2, 3.2, titleX="lept_phi1", units="GeV", keys=hist_keys).clone()
h_lept_phi2 = book_hist_dict(32, -3.2, 3.2, titleX="lept_phi2", units="GeV", keys=hist_keys).clone()

h_mass_WV = book_hist_dict(50, 0, 2500, titleX="mass_WV", units="GeV", keys=hist_keys).clone()
h_mass_ZV = book_hist_dict(50, 0, 2500, titleX="mass_ZV", units="GeV", keys=hist_keys).clone()

# fill ROOT histogram with numpy array
# ===================================
def fill_hist_array(hist, array, weight=1.0):
    
    if len(array) == 0:
        return None
    
    if type(weight) == float:
        hist.FillN(
            len(array),
            np.array(array, np.float64),
            np.full(array.shape, weight)
        )

    else:
        hist.FillN(
            len(array),
            np.array(array, np.float64),
            np.array(weight, np.float64)
        )
    
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
            (df["pfMET_Corr"] > 80) &
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
            (df["pfMET_Corr"] > 50) &
            (np.abs(df["l_eta1"]) < 2.4)
        )

        mu_channel2 = (np.abs(df["l_eta2"]) < 2.4)

        signal_region_loose = (
            (df["isResolved"] == False) &
            (df["ungroomed_PuppiAK8_jet_pt"] > 200 ) &
            (np.abs(df["ungroomed_PuppiAK8_jet_eta"]) < 2.4 ) &
            (df["PuppiAK8_jet_tau2tau1"] < 0.55) &
            (df["PuppiAK8_jet_mass_so_corr"] > 65) &
            (df["PuppiAK8_jet_mass_so_corr"] < 105) &
            (df["vbf_maxpt_jj_m"] > 300) &
            (np.abs(df["vbf_maxpt_j2_eta"] - df["vbf_maxpt_j1_eta"]) > 2.0)
        )
        
        signal_region_tight = (
            (df["isResolved"] == False) &
            (df["ungroomed_PuppiAK8_jet_pt"] > 200 ) &
            (np.abs(df["ungroomed_PuppiAK8_jet_eta"]) < 2.4 ) &
            (df["PuppiAK8_jet_tau2tau1"] < 0.55) &
            (df["PuppiAK8_jet_mass_so_corr"] > 65) &
            (df["PuppiAK8_jet_mass_so_corr"] < 105) &
            (df["vbf_maxpt_jj_m"] > 800) &
            (np.abs(df["vbf_maxpt_j2_eta"] - df["vbf_maxpt_j1_eta"]) > 4.0)
        )
            
        if args.boson == "W":

            boson_channel_sel = W_channel
            
            if args.channel == "mu":
                
                lep_channel_sel = mu_channel
            
            if args.channel == "e":
                
                lep_channel_sel = e_channel
            
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

out_hist_file.Write()
out_hist_file.Close()

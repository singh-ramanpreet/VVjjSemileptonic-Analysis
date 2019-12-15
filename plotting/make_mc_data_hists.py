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
    def __init__(self, xbins, xlow=0, xup=1, titleX="",
                 ybins=None, ylow=None, yup=None, titleY="",
                 keys=[], keys_sub=[]):
        self.xbins = xbins
        self.xlow = xlow
        self.xup = xup
        self.titleX = titleX
        self.ybins = ybins
        self.ylow = ylow
        self.yup = yup
        self.titleY = titleY
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
            titleY = f"Events/{bw}"
        else:
            titleY = "Events"

        variable.SetTitle(f"{titleX};{titleX};{titleY}")
        variable.SetName(titleX)

        return variable

    def hist_2D(self):
        if type(self.xbins) == int:

            if type(self.ybins) == int:
                variable = ROOT.TH2F("", "", self.xbins, self.xlow, self.xup,
                                     self.ybins, self.ylow, self.yup)

            elif type(self.ybins) == np.ndarray:
                variable = ROOT.TH2F("", "", self.xbins, self.xlow, self.xup,
                                     len(self.ybins) - 1, self.ybins.astype(np.float64))

        elif type(self.xbins) == np.ndarray:
            if type(self.ybins) == int:
                variable = ROOT.TH2F("", "", len(self.xbins) - 1, self.xbins.astype(np.float64),
                                     self.ybins, self.ylow, self.yup)

            elif type(self.ybins) == np.ndarray:
                variable = ROOT.TH2F("", "", len(self.xbins) - 1, self.xbins.astype(np.float64),
                                     len(self.ybins) - 1, self.ybins.astype(np.float64))

        else:
            return None

        titleX = self.titleX
        titleY = self.titleY

        variable.SetTitle(f"{titleX}_{titleY};{titleX};{titleY}")
        variable.SetName(f"{titleX}_{titleY}")

        return variable

    def clone(self):

        if self.ybins is None:
            hist_ = self.hist_1D()
        else:
            hist_ = self.hist_2D()

        hist_dict = {}

        for key in self.keys:
            name_ = f"{key}_{hist_.GetName()}"
            hist_dict[key] = hist_.Clone()
            hist_dict[key].SetName(name_)

            for key_sub in self.keys_sub:
                name = f"{name_}_{key_sub}"
                hist_dict[f"{key}_{key_sub}"] = hist_.Clone()
                hist_dict[f"{key}_{key_sub}"].SetName(name)

        return hist_dict

# book histograms
# ===============

# xbins, xlow, xup, variable
hists_1D = [
    (30, 0, 300, "lept_pt1"),
    #(30, 0, 300, "lept_pt2"),
    (25, -2.5, 2.5, "lept_eta1"),
    #(25, -2.5, 2.5, "lept_eta2"),
    (32, -3.2, 3.2, "lept_phi1"),
    #(32, -3.2, 3.2, "lept_phi2"),
    (50, 40.0, 150.0, "PuppiAK8_jet_mass_so_corr"),
    (80, 200.0, 600.0, "ungroomed_PuppiAK8_jet_pt"),
    (50, 0, 2500, "mWV"),
    #(50, 0, 2500, "mZV"),
    (40, 0.0, 0.5, "PuppiAK8jet_n2_sdb1"),
    (40, 0.0, 0.4, "PuppiAK8jet_n2_sdb2"),
    (40, 0.0, 1.0, "PuppiAK8jet_tau2tau1"),
]

hists_2D = [
    (40, 0.0, 0.5, "n2_sdb1",
     40, 0.0, 1.0, "tau2tau1"),
    (40, 0.0, 0.4, "n2_sdb2",
     40, 0.0, 1.0, "tau2tau1"),
]

hist_keys = list(samples_dict.keys())

ROOT.TH1.SetDefaultSumw2()

for histogram in hists_1D:
    make_hists = (
        f"h_{histogram[3]} = book_hist_dict("
        f"xbins=histogram[0], xlow=histogram[1],"
        f"xup=histogram[2], titleX=histogram[3],"
        f"keys=hist_keys)"
    )
    exec(f"{make_hists}.clone()")

for histogram in hists_2D:
    make_hists = (
        f"h2_{histogram[3]}_{histogram[7]} = book_hist_dict("
        f"xbins=histogram[0], xlow=histogram[1],"
        f"xup=histogram[2], titleX=histogram[3],"
        f"ybins=histogram[4], ylow=histogram[5],"
        f"yup=histogram[6], titleY=histogram[7],"
        f"keys=hist_keys)"
    )
    exec(f"{make_hists}.clone()")

# fill ROOT histogram with numpy array
# ===================================
def fill_hist_1d(hist, array, weight=1.0, overflow_in_last_bin=False):

    if len(array) == 0:
        return None

    if type(weight) == float:
        for v in array:
            hist.Fill(v, weight)

    else:
        for v, w in zip(array, weight):
            hist.Fill(v, w)

    if overflow_in_last_bin:
        last_bin = hist.GetNbinsX()
        last_content = hist.GetBinContent(last_bin)
        overflow_bin = last_bin + 1
        overflow_content = hist.GetBinContent(overflow_bin)

        hist.SetBinContent(last_bin, last_content + overflow_content)

    return None

def fill_hist_2d(hist, array1, array2, weight=1.0):

    if len(array1) == 0:
        return None

    if type(weight) == float:
        for v1, v2 in zip(array1, array2):
            hist.Fill(v1, v2, weight)

    else:
        for v1, v2, w in zip(array1, array2, weight):
            hist.Fill(v1, v2, w)

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

        region_loose_no_V_mass_cut = (
            (df["isResolved"] == False) &
            (df["ungroomed_PuppiAK8_jet_pt"] > 200 ) &
            (np.abs(df["ungroomed_PuppiAK8_jet_eta"]) < 2.4 ) &
            #(df["PuppiAK8_jet_tau2tau1"] < 0.55) &
            #(df["PuppiAK8_jet_mass_so_corr"] > 65) &
            #(df["PuppiAK8_jet_mass_so_corr"] < 105) &
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

        if args.region == "loose_no_V_mass_cut":

            region_sel = region_loose_no_V_mass_cut

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
        fill_hist_1d(h_lept_pt1[key], lept_pt1, total_weight)

        #lept_pt2 = skim_df["l_pt2"]
        #fill_hist_1d(h_lept_pt2[key], lept_pt2, total_weight)

        lept_eta1 = skim_df["l_eta1"]
        fill_hist_1d(h_lept_eta1[key], lept_eta1, total_weight)

        #lept_eta2 = skim_df["l_eta2"]
        #fill_hist_1d(h_lept_eta2[key], lept_eta2, total_weight)

        lept_phi1 = skim_df["l_phi1"]
        fill_hist_1d(h_lept_phi1[key], lept_phi1, total_weight)

        #lept_phi2 = skim_df["l_phi2"]
        #fill_hist_1d(h_lept_phi2[key], lept_phi2, total_weight)

        mWV = skim_df["mass_lvj_type0_PuppiAK8"]
        fill_hist_1d(h_mWV[key], mWV, total_weight)

        #mZV = skim_df["mass_llj_PuppiAK8"]
        #fill_hist_1d(h_mZV[key], mZV, total_weight)

        PuppiAK8jet_e2_sdb1 = skim_df["PuppiAK8jet_e2_sdb1"]
        PuppiAK8jet_e2_sdb2 = skim_df["PuppiAK8jet_e2_sdb2"]

        PuppiAK8jet_e3_v2_sdb1 = skim_df["PuppiAK8jet_e3_v2_sdb1"]
        PuppiAK8jet_e3_v2_sdb2 = skim_df["PuppiAK8jet_e3_v2_sdb2"]

        PuppiAK8jet_n2_sdb1 = PuppiAK8jet_e3_v2_sdb1 / (PuppiAK8jet_e2_sdb1)**2
        fill_hist_1d(h_PuppiAK8jet_n2_sdb1[key], PuppiAK8jet_n2_sdb1, total_weight)

        PuppiAK8jet_n2_sdb2 = PuppiAK8jet_e3_v2_sdb2 / (PuppiAK8jet_e2_sdb2)**2
        fill_hist_1d(h_PuppiAK8jet_n2_sdb2[key], PuppiAK8jet_n2_sdb2, total_weight)

        PuppiAK8jet_tau2tau1 = skim_df["PuppiAK8_jet_tau2tau1"]
        fill_hist_1d(h_PuppiAK8jet_tau2tau1[key], PuppiAK8jet_tau2tau1, total_weight)

        fill_hist_2d(h2_n2_sdb1_tau2tau1[key], PuppiAK8jet_n2_sdb1, PuppiAK8jet_tau2tau1, total_weight)
        fill_hist_2d(h2_n2_sdb2_tau2tau1[key], PuppiAK8jet_n2_sdb2, PuppiAK8jet_tau2tau1, total_weight)

        PuppiAK8_jet_mass_so_corr = skim_df["PuppiAK8_jet_mass_so_corr"]
        fill_hist_1d(h_PuppiAK8_jet_mass_so_corr[key], PuppiAK8_jet_mass_so_corr, total_weight, overflow_in_last_bin=True)

        ungroomed_PuppiAK8_jet_pt = skim_df["ungroomed_PuppiAK8_jet_pt"]
        fill_hist_1d(h_ungroomed_PuppiAK8_jet_pt[key], ungroomed_PuppiAK8_jet_pt, total_weight, overflow_in_last_bin=True)

# write hists to root file
# ========================
out_hist_file = ROOT.TFile(f"{args.region}_{args.boson}_{args.channel}.root", "RECREATE")
out_hist_file.cd()

for k in samples_dict:

    for histogram in hists_1D:
        exec(f"h_{histogram[3]}[k].Write()")

    for histogram in hists_2D:
        exec(f"h2_{histogram[3]}_{histogram[7]}[k].Write()")

out_hist_file.Write()
out_hist_file.Close()

#!/usr/bin/env python3

import sys
import os
import json
import numpy as np
import ROOT
import awkward
import uproot
import argparse
import importlib

parser = argparse.ArgumentParser()

parser.add_argument(
    "--datasets", type=str, default="../datasets_2016.json",
    help="json file containing info of datasets, default=%(default)s"
    )

parser.add_argument(
    "--lepton", type=str, default="m",
    help="muon or electron channel, default=%(default)s"
    )

parser.add_argument(
    "--boson", type=str, default="W",
    help="W or Z, default=%(default)s"
    )

parser.add_argument(
    "--region", type=str, default="signal_loose_W",
    help="region , default=%(default)s"
    )

parser.add_argument(
    "--output", type=str, default="",
    help="output filename, default='region'_'lepton'.root"
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
    (40, 0, 2000, "lept_pt1"),
    #(30, 0, 300, "lept_pt2"),
    (26, -2.6, 2.6, "lept_eta1"),
    #(25, -2.5, 2.5, "lept_eta2"),
    (34, -3.4, 3.4, "lept_phi1"),
    #(32, -3.2, 3.2, "lept_phi2"),
    (20, 0, 1000, "pfMET_Corr"),
    (34, -3.4, 3.4, "pfMET_Corr_phi"),
    # ak8 jet
    (80, 0.0, 400.0, "PuppiAK8_jet_mass_so_corr"),
    (80, 200.0, 2000.0, "ungroomed_PuppiAK8_jet_pt"),
    (26, -2.6, 2.6, "ungroomed_PuppiAK8_jet_eta"),
    (34, -3.4, 3.4, "ungroomed_PuppiAK8_jet_phi"),
    (40, 0.0, 0.5, "PuppiAK8jet_n2_sdb1"),
    (40, 0.0, 0.4, "PuppiAK8jet_n2_sdb2"),
    (40, 0.0, 1.0, "PuppiAK8jet_tau2tau1"),
    # W
    (50, 0.0, 2000.0, "v_pt_type0"),
    (51, -5.1, 5.1, "v_eta_type0"),
    (40, 0.0, 2000.0, "v_mt_type0"),
    # vbf jets
    (120, 0.0, 2000.0, "vbf_maxpt_j1_pt"),
    (40, 0.0, 2000.0, "vbf_maxpt_j2_pt"),
    (51, -5.1, 5.1, "vbf_maxpt_j1_eta"),
    (51, -5.1, 5.1, "vbf_maxpt_j2_eta"),
    (20, 0.0, 10.0, "vbf_maxpt_jj_Deta"),
    (34, -3.4, 3.4, "vbf_maxpt_j1_phi"),
    (34, -3.4, 3.4, "vbf_maxpt_j2_phi"),
    (40, 500.0, 2500.0, "vbf_maxpt_jj_m"),
    #
    (60, -6.0, 6.0, "BosonCentrality_type0"),
    (60, -6.0, 6.0, "ZeppenfeldWL_type0"),
    (60, -6.0, 6.0, "ZeppenfeldWH"),
    # W V system
    (50, 0, 2500, "mass_lvj_type0_PuppiAK8"),
    (np.array([600, 700, 800, 900,
               1000, 1200, 1500, 2000, 2500]), 0, 0, "mass_lvj_type0_PuppiAK8_8bin"),
    (60, 0.0, 600.0, "pt_lvj_type0_PuppiAK8"),
    (20, -5.0, 5.0, "eta_lvj_type0_PuppiAK8"),
    (34, -3.4, 3.4, "phi_lvj_type0_PuppiAK8"),
    #(50, 0, 2500, "mZV"),
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
        hist.SetBinContent(overflow_bin, 0.0)

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

# total raw entries in data sets
total_entries = book_hist_dict(xbins=1, titleX="total_entries").hist_1D()
total_entries.SetCanExtend(ROOT.TH1.kAllAxes)

# selection code import
sel_code = importlib.import_module(f"selections.{args.region}")

lep_channel = {
    "e": sel_code.e_channel,
    "m": sel_code.m_channel
}

if args.boson == "Z":
    lep_channel2 = {
        "e": sel_code.e_channel2,
        "m": sel_code.m_channel2
    }

region_ = sel_code.region_
apply_btag0Wgt = sel_code.apply_btag0Wgt

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

        if "data" in key:
            df["btag0Wgt"] = 1.0

        lep_sel = lep_channel[args.lepton](df)
        region_sel = region_(df, args.lepton)

        if args.boson == "W":
            skim_df = df[lep_sel & region_sel]
            total_weight = xs_weight * skim_df["genWeight"] * skim_df["trig_eff_Weight"] \
                            * skim_df["id_eff_Weight"] * skim_df["pu_Weight"]

        if args.boson == "Z":
            lep_sel2 = lep_channel2[args.lepton](df)
            skim_df = df[lep_sel & lep_sel2 & region_sel]
            total_weight = xs_weight * skim_df["genWeight"] * skim_df["trig_eff_Weight"] * skim_df["trig_eff_Weight2"] \
                            * skim_df["id_eff_Weight"] * skim_df["id_eff_Weight2"] * skim_df["pu_Weight"]

        if apply_btag0Wgt:
            total_weight = total_weight * skim_df["btag0Wgt"]

        print("filling hists .... ")

        if "data" in key:
            total_entries.Fill("data", len(skim_df))

        else:
            total_entries.Fill(key, len(skim_df))

        lept_pt1 = skim_df["l_pt1"]
        fill_hist_1d(h_lept_pt1[key], lept_pt1, total_weight, overflow_in_last_bin=True)

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

        pfMET_Corr = skim_df["pfMET_Corr"]
        fill_hist_1d(h_pfMET_Corr[key], pfMET_Corr, total_weight, overflow_in_last_bin=True)

        pfMET_Corr_phi = skim_df["pfMET_Corr_phi"]
        fill_hist_1d(h_pfMET_Corr_phi[key], pfMET_Corr_phi, total_weight)

        PuppiAK8_jet_mass_so_corr = skim_df["PuppiAK8_jet_mass_so_corr"]
        fill_hist_1d(h_PuppiAK8_jet_mass_so_corr[key], PuppiAK8_jet_mass_so_corr, total_weight, overflow_in_last_bin=True)

        ungroomed_PuppiAK8_jet_pt = skim_df["ungroomed_PuppiAK8_jet_pt"]
        fill_hist_1d(h_ungroomed_PuppiAK8_jet_pt[key], ungroomed_PuppiAK8_jet_pt, total_weight, overflow_in_last_bin=True)

        ungroomed_PuppiAK8_jet_eta = skim_df["ungroomed_PuppiAK8_jet_eta"]
        fill_hist_1d(h_ungroomed_PuppiAK8_jet_eta[key], ungroomed_PuppiAK8_jet_eta, total_weight)

        ungroomed_PuppiAK8_jet_phi = skim_df["ungroomed_PuppiAK8_jet_phi"]
        fill_hist_1d(h_ungroomed_PuppiAK8_jet_phi[key], ungroomed_PuppiAK8_jet_phi, total_weight)

        PuppiAK8jet_e2_sdb1 = skim_df["PuppiAK8jet_e2_sdb1"]
        PuppiAK8jet_e2_sdb2 = skim_df["PuppiAK8jet_e2_sdb2"]

        PuppiAK8jet_e3_v2_sdb1 = skim_df["PuppiAK8jet_e3_v2_sdb1"]
        PuppiAK8jet_e3_v2_sdb2 = skim_df["PuppiAK8jet_e3_v2_sdb2"]

        PuppiAK8jet_n2_sdb1 = PuppiAK8jet_e3_v2_sdb1 / (PuppiAK8jet_e2_sdb1)**2
        fill_hist_1d(h_PuppiAK8jet_n2_sdb1[key], PuppiAK8jet_n2_sdb1, total_weight, overflow_in_last_bin=True)

        PuppiAK8jet_n2_sdb2 = PuppiAK8jet_e3_v2_sdb2 / (PuppiAK8jet_e2_sdb2)**2
        fill_hist_1d(h_PuppiAK8jet_n2_sdb2[key], PuppiAK8jet_n2_sdb2, total_weight, overflow_in_last_bin=True)

        PuppiAK8jet_tau2tau1 = skim_df["PuppiAK8_jet_tau2tau1"]
        fill_hist_1d(h_PuppiAK8jet_tau2tau1[key], PuppiAK8jet_tau2tau1, total_weight, overflow_in_last_bin=True)

        v_pt_type0 = skim_df["v_pt_type0"]
        fill_hist_1d(h_v_pt_type0[key], v_pt_type0, total_weight, overflow_in_last_bin=True)

        v_eta_type0 = skim_df["v_eta_type0"]
        fill_hist_1d(h_v_eta_type0[key], v_eta_type0, total_weight)

        v_mt_type0 = skim_df["v_mt_type0"]
        fill_hist_1d(h_v_mt_type0[key], v_mt_type0, total_weight, overflow_in_last_bin=True)

        vbf_maxpt_j1_pt = skim_df["vbf_maxpt_j1_pt"]
        fill_hist_1d(h_vbf_maxpt_j1_pt[key], vbf_maxpt_j1_pt, total_weight, overflow_in_last_bin=True)

        vbf_maxpt_j2_pt = skim_df["vbf_maxpt_j2_pt"]
        fill_hist_1d(h_vbf_maxpt_j2_pt[key], vbf_maxpt_j2_pt, total_weight, overflow_in_last_bin=True)

        vbf_maxpt_j1_eta = skim_df["vbf_maxpt_j1_eta"]
        fill_hist_1d(h_vbf_maxpt_j1_eta[key], vbf_maxpt_j1_eta, total_weight)

        vbf_maxpt_j2_eta = skim_df["vbf_maxpt_j2_eta"]
        fill_hist_1d(h_vbf_maxpt_j2_eta[key], vbf_maxpt_j2_eta, total_weight)

        vbf_maxpt_j1_phi = skim_df["vbf_maxpt_j1_phi"]
        fill_hist_1d(h_vbf_maxpt_j1_phi[key], vbf_maxpt_j1_phi, total_weight)

        vbf_maxpt_j2_phi = skim_df["vbf_maxpt_j2_phi"]
        fill_hist_1d(h_vbf_maxpt_j2_phi[key], vbf_maxpt_j2_phi, total_weight)

        vbf_maxpt_jj_Deta = skim_df["vbf_maxpt_jj_Deta"]
        fill_hist_1d(h_vbf_maxpt_jj_Deta[key], vbf_maxpt_jj_Deta, total_weight)

        vbf_maxpt_jj_m = skim_df["vbf_maxpt_jj_m"]
        fill_hist_1d(h_vbf_maxpt_jj_m[key], vbf_maxpt_jj_m, total_weight)

        BosonCentrality_type0 = skim_df["BosonCentrality_type0"]
        fill_hist_1d(h_BosonCentrality_type0[key], BosonCentrality_type0, total_weight)

        ZeppenfeldWL_type0 = skim_df["ZeppenfeldWL_type0"]
        fill_hist_1d(h_ZeppenfeldWL_type0[key], ZeppenfeldWL_type0, total_weight)

        ZeppenfeldWH = skim_df["ZeppenfeldWH"]
        fill_hist_1d(h_ZeppenfeldWH[key], ZeppenfeldWH, total_weight)

        mass_lvj_type0_PuppiAK8 = skim_df["mass_lvj_type0_PuppiAK8"]
        fill_hist_1d(h_mass_lvj_type0_PuppiAK8[key], mass_lvj_type0_PuppiAK8, total_weight, overflow_in_last_bin=True)

        mass_lvj_type0_PuppiAK8_8bin = skim_df["mass_lvj_type0_PuppiAK8"]
        fill_hist_1d(h_mass_lvj_type0_PuppiAK8_8bin[key], mass_lvj_type0_PuppiAK8_8bin, total_weight, overflow_in_last_bin=True)

        pt_lvj_type0_PuppiAK8 = skim_df["pt_lvj_type0_PuppiAK8"]
        fill_hist_1d(h_pt_lvj_type0_PuppiAK8[key], pt_lvj_type0_PuppiAK8, total_weight, overflow_in_last_bin=True)

        eta_lvj_type0_PuppiAK8 = skim_df["eta_lvj_type0_PuppiAK8"]
        fill_hist_1d(h_eta_lvj_type0_PuppiAK8[key], eta_lvj_type0_PuppiAK8, total_weight)

        phi_lvj_type0_PuppiAK8 = skim_df["phi_lvj_type0_PuppiAK8"]
        fill_hist_1d(h_phi_lvj_type0_PuppiAK8[key], phi_lvj_type0_PuppiAK8, total_weight)

        # 2D hists
        fill_hist_2d(h2_n2_sdb1_tau2tau1[key], PuppiAK8jet_n2_sdb1, PuppiAK8jet_tau2tau1, total_weight)
        fill_hist_2d(h2_n2_sdb2_tau2tau1[key], PuppiAK8jet_n2_sdb2, PuppiAK8jet_tau2tau1, total_weight)

# write hists to root file
# ========================

if args.output == "":
    out_hist_filename = f"{args.region}_{args.lepton}.root"
else:
    out_hist_filename = args.output

out_hist_file = ROOT.TFile(out_hist_filename, "recreate")
out_hist_file.cd()

for k in samples_dict:

    for histogram in hists_1D:
        exec(f"h_{histogram[3]}[k].Write()")

    for histogram in hists_2D:
        exec(f"h2_{histogram[3]}_{histogram[7]}[k].Write()")

total_entries.Write()

out_hist_file.Write()
out_hist_file.Close()

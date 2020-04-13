#!/usr/bin/env python3

import sys
import os
import json
import numpy as np
import ROOT
ROOT.PyConfig.IgnoreCommandLineOptions = True
import awkward
import uproot
import argparse
import importlib
from root_numpy.tmva import evaluate_reader
from array import array

parser = argparse.ArgumentParser()

parser.add_argument(
    "--datasets", type=str, default="../datasets_2016.json",
    help="json file containing info of datasets, default=%(default)s"
    )

parser.add_argument(
    "--variables", type=str, default="../variables_map.json",
    help="json file: variables central and systematic map, default=%(default)s"
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
    "--region", type=str, default="training_02_WV",
    help="region , default=%(default)s"
    )

parser.add_argument(
    "--output", type=str, default="",
    help="output filename, default='region'_'info_out'_'lepton'.root"
    )

parser.add_argument(
    "--mva", type=str, default="",
    help="mva training weight file (xml), default=%(default)s"
    )

parser.add_argument(
    "--mva-var-list", dest="var_list", type=str, default="",
    help="mva training variable list, default=%(default)s"
    )

parser.add_argument(
    "--info-out", dest="info_out", type=str, default="theoryUnc",
    help="additional string in output filename, default=%(default)s"
    )

parser.add_argument(
    "--apply-L1PF", dest="apply_L1PF", action="store_true",
    help="apply L1 pre-fire weight, default=%(default)s"
    )

args = parser.parse_args()

# samples dict
# ============
samples_dict = json.load(open(args.datasets, "r"))

# variables
# ===========
variables_mapped = {}
variables_map = json.load(open(args.variables, "r"))

for name_ in variables_map:
    variables_mapped[name_] = variables_map[name_]["central"]

# TMVA Reader
variables = open(args.var_list).readlines()
variables = [i.rstrip("\n") for i in variables]

mva_reader = ROOT.TMVA.Reader()

for var in variables:
    mva_reader.AddVariable(var, array("f", [-999.0]))

mva_reader.BookMVA("BDT", args.mva)

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
    (40, -1.0, 1.0, "mva_score"),
    (30, -1.0, 1.0, "mva_score_30bin"),
    (20, -1.0, 1.0, "mva_score_20bin"),
    (10, -1.0, 1.0, "mva_score_10bin"),
    (34, -1.0, 0.7, "mva_score_var1"),
    (np.array([-1.0, -0.300, -0.150, 0.000, 0.100,
               0.200, 0.300, 0.400, 0.500, 0.600, 1]), 0, 0, "mva_score_var10"),
    (np.array([-1.0, -0.300, -0.150, 0.000, 0.100,
               0.200, 0.300, 0.400, 0.500, 0.600, 0.700, 1]), 0, 0, "mva_score_var11"),
    (np.array([-1.0, -0.350, -0.250, -0.150,
               -0.050, -0.000, 0.100, 0.150,
               0.250, 0.300, 0.350, 0.450,
               0.500, 0.600, 0.650, 1]), 0, 0, "mva_score_var15"),
    (np.array([-1.0, -0.400, -0.300, -0.200, -0.150,
               -0.050, -0.000, 0.050, 0.100, 0.150,
               0.200, 0.250, 0.300, 0.350, 0.400,
               0.450, 0.500, 0.550, 0.600, 0.700, 1.0]), 0, 0, "mva_score_var20")
]

hist_keys = list(samples_dict.keys())

qcd_scale_bounding_keys = [f"qcd_scale{j}" for j in [1,2,3,4,6,8]] + ["qcd_scaleUp", "qcd_scaleDown"]
pdf_scale_bounding_keys = [f"pdf_scale{j}" for j in range(1, 100)] + ["pdf_scaleUp", "pdf_scaleDown"]

scale_bounding_keys = qcd_scale_bounding_keys + pdf_scale_bounding_keys
print(scale_bounding_keys)
ROOT.TH1.SetDefaultSumw2()

for histogram in hists_1D:
    make_hists = (
        f"h_{histogram[3]} = book_hist_dict("
        f"xbins=histogram[0], xlow=histogram[1],"
        f"xup=histogram[2], titleX=histogram[3],"
        f"keys=hist_keys, keys_sub=scale_bounding_keys)"
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

# add selection code to root file
code_text = open(f"selections/{args.region}.py").read()
ttext = ROOT.TText(0.0, 0.0, "\n" + code_text)
ttext.SetName("selection_code")

# loop over samples, apply selections,
# and fill histograms.
# ===================================
for key in samples_dict:

    location = samples_dict[key]["location"]
    filelist = samples_dict[key]["filelist"]
    lumi = samples_dict[key]["lumi"]

    if key == "data_obs": continue
    if key == "Top": continue
    if key == "QCD": continue
    if key == "DYJets": continue
    if key == "WJets": continue

    for sample in filelist:

        root_file = location + sample["name"]
        xs = sample["xs"]
        nMC = sample["nMC"]
        nMCneg = sample["nMCneg"]

        if nMC == 0:
            file_ = ROOT.TFile.Open(root_file)
            total_events_hist = file_.Get("TotalEvents")
            nMCneg = total_events_hist.GetBinContent(1)
            nMC = total_events_hist.GetBinContent(2)
            print(nMC, nMCneg)

        xs_weight = (lumi * xs) / (nMC - (2 * nMCneg))

        print("loading ... ", key, sample["name"])

        df = uproot.lazyarrays(root_file, "Events", basketcache=uproot.cache.ThreadSafeArrayCache(100*1024**2))
        
        for new_name, var_name in variables_mapped.items():
            df[new_name] = df[var_name]

        # some derived columns
        df["vbf_jj_Deta"] = np.abs(df["vbf_j1_eta"] - df["vbf_j2_eta"])
        df["fatjet_n2b1"] = df["fatjet_e3_v2_sdb1"] / (df["fatjet_e2_sdb1"])**2
        df["fatjet_n2b2"] = df["fatjet_e3_v2_sdb2"] / (df["fatjet_e2_sdb2"])**2
        df["ht"] = df["fatjet_pt"] + df["vbf_j1_pt"] + df["vbf_j2_pt"]
        df["ht_resolved"] = df["dijet_j1_pt"] + df["dijet_j2_pt"] + df["vbf_j1_pt"] + df["vbf_j2_pt"]
        df["zeppenfeld_w_Deta"] = df["zeppenfeld_w"] / df["vbf_jj_Deta"]
        df["zeppenfeld_v_Deta"] = df["zeppenfeld_v"] / df["vbf_jj_Deta"]

        df["lept_channel"] = (df["lept1_m"] != 0.1056583745).astype(int)
        df["v_mt"] = np.sqrt(df["v_m"]**2 + df["v_pt"]**2)

        # till they are available
        df["trig_eff_weight"] = 1.0
        df["trig_eff_weight2"] = 1.0
        df["btag0_weight"] = 1.0

        if "data" in key:
            df["gen_weight"] = 1.0
            df["pu_weight"] = 1.0
            df["pu_weight_up"] = 1.0
            df["pu_weight_down"] = 1.0
            df["trig_eff_weight"] = 1.0
            df["trig_eff_weight2"] = 1.0
            df["id_eff_weight"] = 1.0
            df["id_eff_weight2"] = 1.0
            df["btag0_weight"] = 1.0
            df["L1PFWeight"] = 1.0

        lep_sel = lep_channel[args.lepton](df)
        region_sel = region_(df, args.lepton)

        var_data = np.column_stack(tuple([df[var] for var in variables]))
        mva_score = evaluate_reader(mva_reader, "BDT", var_data)
        df["mva_score"] = mva_score

        if args.boson == "W":
            skim_df = df[lep_sel & region_sel]
            total_weight = xs_weight * skim_df["gen_weight"] * skim_df["trig_eff_weight"] \
                            * skim_df["id_eff_weight"] * skim_df["pu_weight"]

        if args.boson == "Z":
            lep_sel2 = lep_channel2[args.lepton](df)
            skim_df = df[lep_sel & lep_sel2 & region_sel]
            total_weight = xs_weight * skim_df["gen_weight"] * skim_df["trig_eff_weight"] * skim_df["trig_eff_weight2"] \
                            * skim_df["id_eff_weight"] * skim_df["id_eff_weight2"] * skim_df["pu_weight"]

        if apply_btag0Wgt:
            total_weight = total_weight * skim_df["btag0_weight"]

        if args.apply_L1PF:
            print("Applying L1 PreFire weights")
            total_weight = total_weight * skim_df["L1PFWeight"]

        print("filling hists .... ")

        mva_score = skim_df["mva_score"]

        list_of_mva_hists = [f"h_{i[3]}" for i in hists_1D if "mva_score" in i[3]]
        list_of_mva_hists = [eval(i) for i in list_of_mva_hists]

        for histogram in list_of_mva_hists:

            fill_hist_1d(histogram[key], mva_score, total_weight, overflow_in_last_bin=True)

            lhe_weight = skim_df["LHEWeight"]

            j = 0
            for i in range(1, 108):
                if (i == 5) or (i == 7): continue
                if i <= 8:
                    j = i
                    sub_key = "qcd_scale"
                else:
                    j = i - 8
                    sub_key ="pdf_scale"

                new_weight = (lhe_weight[:, i] / lhe_weight[:, 0]) * total_weight

                fill_hist_1d(histogram[f"{key}_{sub_key}{j}"], mva_score, new_weight, overflow_in_last_bin=True)


            nbins = h_mva_score[f"{key}"].GetNbinsX()
            print("nbins", nbins)

            for b in range(1, nbins + 1):
                bin_content = histogram[f"{key}"].GetBinContent(b)
                sys_QCD = 0
                sys_PDF = 0

                for i in range(1, 9):
                    if (i == 5) or (i == 7): continue
                    diff = abs(histogram[f"{key}_qcd_scale{i}"].GetBinContent(b) - bin_content)
                    if diff > sys_QCD:
                        sys_QCD = diff
                print("QCD sys ", sys_QCD)

                histogram[f"{key}_qcd_scaleUp"].SetBinContent(b, histogram[f"{key}"].GetBinContent(b) + sys_QCD)
                histogram[f"{key}_qcd_scaleDown"].SetBinContent(b, histogram[f"{key}"].GetBinContent(b) - sys_QCD)

                print("PDF sys ", sep=" |", end=" ")
                for i in range(1, 100):
                    diff = abs(histogram[f"{key}_pdf_scale{i}"].GetBinContent(b) - bin_content)
                    sys_PDF += diff * diff
                    print(sys_PDF, sep=" |", end=" ")
                
                final_sys_PDF = (sys_PDF/99.0) ** 0.5
                print("Final PDF sys", final_sys_PDF)
                histogram[f"{key}_pdf_scaleUp"].SetBinContent(b, histogram[f"{key}"].GetBinContent(b) + final_sys_PDF)
                histogram[f"{key}_pdf_scaleDown"].SetBinContent(b, histogram[f"{key}"].GetBinContent(b) - final_sys_PDF)

# write hists to root file
# ========================
if args.output == "":
    out_hist_filename = f"{args.region}_{args.lepton}.root"
    if args.info_out != "":
        out_hist_filename = f"{args.region}_{args.info_out}_{args.lepton}.root"
else:
    out_hist_filename = args.output

out_hist_file = ROOT.TFile(out_hist_filename, "recreate")
out_hist_file.cd()

for k in samples_dict:

    for histogram in hists_1D:
        exec(f"h_{histogram[3]}[k].Write()")

        for j in scale_bounding_keys:
            exec(f"h_{histogram[3]}['{k}_{j}'].Write()")

out_hist_file.Write()
out_hist_file.Close()

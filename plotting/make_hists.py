#!/usr/bin/env python3

import ROOT
import numpy as np
import argparse

parser = argparse.ArgumentParser()

parser.add_argument("--base-dir", dest="base_dir", type=str,
                    default="root://cmseos.fnal.gov//store/user/singhr/wv_vbs_ntuples",
                    help="base directory pre-fix, default=%(default)s")

parser.add_argument("--in-dir", dest="in_dir", type=str, default="2018_May11",
                    help="prepared root files dir relative to /store/user/singhr/, default=%(default)s")

parser.add_argument("--regions", action="append", default=[],
                    help="region to produce hists for, default=%(default)s")

parser.add_argument("--output", type=str, default="hists.root",
                    help="hists output filename, default=%(default)s")

parser.add_argument("--threads", type=int, default=4,
                    help="RDataFrame MT threads to use, default=%(default)s")

args = parser.parse_args()

stopwatch = ROOT.TStopwatch()
stopwatch.Start()

ROOT.ROOT.EnableImplicitMT(args.threads)
nThreads = ROOT.ROOT.GetImplicitMTPoolSize()
print(f"Using {nThreads} Threads")
df = ROOT.RDataFrame("Events", f"{args.base_dir}/{args.in_dir}/*.root")
count = df.Count()
total_entries = count.GetValue()

# progress bar
ROOT.gInterpreter.ProcessLine("""
    auto count = (ROOT::RDF::RResultPtr<ULong64_t> *)TPython::Eval("count");
    int total_entries = TPython::Eval("total_entries");
    std::string progress;
    std::mutex bar_mutex;
    auto bar_print = [&progress, &bar_mutex](unsigned int, ULong64_t &)
    {
        std::lock_guard<std::mutex> lg(bar_mutex);
        progress.push_back('#');
        std::cout << "\\r[" << std::left << std::setw(100) << progress << "]" << std::flush;
    };
    count->OnPartialResultSlot(total_entries / 100, bar_print);
""")

WJets_type = "WJets_HT"
DYJets_type = "DYJets_HT"
samples_name = ["data_obs", "VBS_EWK", "VBS_QCD", "Top", WJets_type, DYJets_type]


# define weight columns
#######################
weight_w = "xs_weight * gen_weight"
if "2017" in args.in_dir:
    weight_w = "L1PFWeight * " + weight_w
weight_z =  "xs_weight * gen_weight * pu_weight * lept1_id_eff_weight * lept2_id_eff_weight"

if any(x in i for x in ["zv", "zjj"] for i in args.regions):
    total_weight = weight_z
else:
    total_weight = weight_w
print("Weight >>> ", total_weight)

list_of_weight_col = {
    "total_weight": total_weight,
}

if any("qcd" in i for i in args.regions):
    for i in range(45):
        list_of_weight_col[f"total_weight_qcd_{i}"] = f"{total_weight} * scaleWeight[{i}]"

if any("pdf" in i for i in args.regions):
    for i in range(104):
        list_of_weight_col[f"total_weight_pdf_{i}"] = f"{total_weight} * pdfWeight[{i}]"

# start with main df
df_with_weight_cols = [df]
for col_name in list_of_weight_col:
    df_with_weight_cols.append(df_with_weight_cols[-1].Define(col_name, list_of_weight_col[col_name]))

#######################

# separate out dataframes by sample tag
df_samples = {}
for sample_ in samples_name:
    df_samples[sample_] = df_with_weight_cols[-1].Filter(f"sample_tag == \"{sample_}\"")


# split W + Jets
w_resolved_split = {
    "r1": "vbf_jj_Deta < 5 && vbf_j1_pt < 75",
    "r2": "vbf_jj_Deta >= 5 && vbf_j1_pt < 75",
    "r3": "vbf_jj_Deta < 4 && vbf_j1_pt >= 75 && vbf_j1_pt <= 150",
    "r4": "vbf_jj_Deta >= 4 && vbf_j1_pt >= 75 && vbf_j1_pt <= 150",
    "r5": "vbf_j1_pt > 150"
}

w_boosted_split = {
    "b1": "vbf_jj_Deta < 5",
    "b2": "vbf_jj_Deta >= 5"
}

if "wjj" in args.regions[0]:
    w_split = w_resolved_split

if "wv" in args.regions[0]:
    w_split = w_boosted_split

if ("wjj" in args.regions[0]) or ("wv" in args.regions[0]):
    for i, j in w_split.items():
        samples_name.append(f"{WJets_type}_{i}")
        df_samples[f"{WJets_type}_{i}"] = df_with_weight_cols[-1].Filter(f"sample_tag == \"{WJets_type}\" && {j}")

selections = {}
selections["el_ch"] = "lept_channel == 1 && fabs(lept1_eta) < 2.5 && !(fabs(lept1_eta) > 1.4442 && fabs(lept1_eta) < 1.566)"
selections["el2_ch"] = selections["el_ch"].replace("lept1", "lept2")

selections["mu_ch"] = "lept_channel == 0 && fabs(lept1_eta) < 2.4"
selections["mu2_ch"] = selections["mu_ch"].replace("lept1", "lept2")

selections["z_ch"] = "lept1_pt > LEPT1_PT_CUT && lept2_pt > LEPT2_PT_CUT" \
                     " && lept1_q * lept2_q < 0" \
                     " && v_m > 75 && v_m < 105"

selections["w_ch"] = "lept1_pt > LEPT1_PT_CUT && pf_met_corr > MET_CUT" \
                     " && lept2_pt < 0"

selections["z_mu_ch"] = selections["z_ch"] + " && " + selections["mu_ch"] + " && " + selections["mu2_ch"]
selections["z_el_ch"] = selections["z_ch"] + " && " + selections["el_ch"] + " && " + selections["el2_ch"]

selections["w_mu_ch"] = selections["w_ch"] + " && " + selections["mu_ch"]
selections["w_el_ch"] = selections["w_ch"] + " && " + selections["el_ch"]

selections["vbf_jets"] = "vbf_jj_m > 500" \
                         " && vbf_j1_pt > 50" \
                         " && vbf_j2_pt > 50" \
                         " && vbf_jj_Deta > 2.5"

selections["resolved_jets"] = "dijet_pt > 0" \
                                " && dijet_j2_pt > 30" \
                                " && dijet_j1_pt > 30" \
                                " && dijet_m > 65 && dijet_m < 105"

selections["resolved_jets_sb"] = "dijet_pt > 0" \
                                " && dijet_j2_pt > 30" \
                                " && dijet_j1_pt > 30" \
                                " && ((dijet_m > 40 && dijet_m < 65) || (dijet_m > 105 && dijet_m < 150))"

selections["boosted_jets"] = "fatjet_pt > 200" \
                                " && fabs(fatjet_eta) < 2.4" \
                                " && fatjet_tau21 < 0.55" \
                                " && fatjet_m > 65 && fatjet_m < 105"

selections["boosted_jets_sb"] = "fatjet_pt > 200" \
                                " && fabs(fatjet_eta) < 2.4" \
                                " && fatjet_tau21 < 0.55" \
                                " && ((fatjet_m > 40 && fatjet_m < 65) || (fatjet_m > 105 && fatjet_m < 150))"


##############
### ZJJ
selections["z_common_m"] = selections["z_mu_ch"].replace("LEPT1_PT_CUT", "35").replace("LEPT2_PT_CUT", "20") \
                            + " && " + selections["vbf_jets"] \
                            + " && nBTagJet_loose == 0"

selections["z_common_e"] = selections["z_el_ch"].replace("LEPT1_PT_CUT", "35").replace("LEPT2_PT_CUT", "20") \
                            + " && " + selections["vbf_jets"] \
                            + " && nBTagJet_loose == 0"

selections["z_common_l"] = "((" + selections["z_common_m"] + ") || (" + selections["z_common_e"] + "))"


selections_regions = {}
for i in ("m", "e", "l"):
    selections_regions[f"sr_zjj_{i}"] = selections[f"z_common_{i}"] + " && " + selections["resolved_jets"]

    selections_regions[f"cr_vjets_zjj_{i}"] = selections[f"z_common_{i}"] + " && " + selections["resolved_jets_sb"]

    selections_regions[f"cr_top_zjj_{i}"] = selections_regions[f"sr_zjj_{i}"].replace("nBTagJet_loose == 0", "nBTagJet_loose > 0")


    ### ZV
    selections_regions[f"sr_zv_{i}"] = selections[f"z_common_{i}"] + " && " + selections["boosted_jets"]

    selections_regions[f"cr_vjets_zv_{i}"] = selections[f"z_common_{i}"] + " && " + selections["boosted_jets_sb"]

    selections_regions[f"cr_top_zv_{i}"] = selections_regions[f"sr_zv_{i}"].replace("nBTagJet_loose == 0", "nBTagJet_loose > 0")

##############
##############
### WJJ
selections["w_common_m"] = selections["w_mu_ch"].replace("LEPT1_PT_CUT", "35").replace("MET_CUT", "30") \
                            + " && " + selections["vbf_jets"] \
                            + " && isAntiIso == 0" \
                            + " && boson_centrality > 0.0" \
                            + " && fabs(zeppenfeld_w_Deta) < 1.0" \
                            + " && fabs(zeppenfeld_v_Deta) < 1.0" \
                            + " && nBTagJet_loose == 0" 

selections["w_common_e"] = selections["w_el_ch"].replace("LEPT1_PT_CUT", "35").replace("MET_CUT", "30") \
                            + " && " + selections["vbf_jets"] \
                            + " && isAntiIso == 0" \
                            + " && boson_centrality > 0.0" \
                            + " && fabs(zeppenfeld_w_Deta) < 1.0" \
                            + " && fabs(zeppenfeld_v_Deta) < 1.0" \
                            + " && nBTagJet_loose == 0"

selections["w_common_l"] = "((" + selections["w_common_m"] + ") || (" + selections["w_common_e"] + "))"


for i in ("m", "e", "l"):
    selections_regions[f"sr_wjj_{i}"] = selections[f"w_common_{i}"] + " && " + selections["resolved_jets"]

    selections_regions[f"cr_vjets_wjj_{i}"] = selections[f"w_common_{i}"] + " && " + selections["resolved_jets_sb"]

    selections_regions[f"cr_top_wjj_{i}"] = selections_regions[f"sr_wjj_{i}"].replace("nBTagJet_loose == 0", "nBTagJet_loose > 0")

    for k, j in w_resolved_split.items():
        selections_regions[f"cr_vjets_{k}_wjj_{i}"] = selections_regions[f"cr_vjets_wjj_{i}"] + " && " + j

    ### WV
    selections_regions[f"sr_wv_{i}"] = selections[f"w_common_{i}"] + " && " + selections["boosted_jets"]

    selections_regions[f"cr_vjets_wv_{i}"] = selections[f"w_common_{i}"] + " && " + selections["boosted_jets_sb"]

    selections_regions[f"cr_top_wv_{i}"] = selections_regions[f"sr_wv_{i}"].replace("nBTagJet_loose == 0", "nBTagJet_loose > 0")

    for k, j in w_boosted_split.items():
        selections_regions[f"cr_vjets_{k}_wv_{i}"] = selections_regions[f"cr_vjets_wv_{i}"] + " && " + j
##############

# jes sys
# make keys

jes_vars = [
    "vbf_jj_m",
    "vbf_j1_pt",
    "vbf_j2_pt",
    "dijet_m",
    "dijet_pt",
    "dijet_j1_pt",
    "dijet_j2_pt",
    "fatjet_pt"
]


# list of regions to make systematic hists
sys_region_list = [
    "sr_wjj_l", "sr_wv_l", "sr_zjj_l", "sr_zv_l",
    "sr_wjj_e", "sr_wv_e", "sr_zjj_e", "sr_zv_e",
    "sr_wjj_m", "sr_wv_m", "sr_zjj_m", "sr_zv_m",
    "cr_vjets_wjj_l", "cr_vjets_wv_l", "cr_vjets_zjj_l", "cr_vjets_zv_l",
    "cr_vjets_wjj_e", "cr_vjets_wv_e", "cr_vjets_zjj_e", "cr_vjets_zv_e",
    "cr_vjets_wjj_m", "cr_vjets_wv_m", "cr_vjets_zjj_m", "cr_vjets_zv_m",
    "cr_top_wjj_l", "cr_top_wv_l", "cr_top_zjj_l", "cr_top_zv_l",
    "cr_top_wjj_e", "cr_top_wv_e", "cr_top_zjj_e", "cr_top_zv_e",
    "cr_top_wjj_m", "cr_top_wv_m", "cr_top_zjj_m", "cr_top_zv_m",
]


#jes_vars_W = ["pf_met_corr"] + jes_vars
jes_vars_W = jes_vars
jes_vars_Z = jes_vars


for jes_sys in ("jesUp", "jesDown"):
    
    for region in sys_region_list:
        
        temp_string = selections_regions[region]
        
        jes_var_replace = []
        if ("wjj" in region) or ("wv" in region):
            jes_var_replace = jes_vars_W

        if ("zjj" in region) or ("zv" in region):
            jes_var_replace = jes_vars_Z

        for jes_var in jes_var_replace:
            temp_string = temp_string.replace(jes_var, f"{jes_var}_{jes_sys}")
    
        selections_regions[f"{region}_{jes_sys}"] =  temp_string

##############
# pdf qcd sys
# make keys

for pdf_qcd_sys in ("pdfUp", "pdfDown", "qcdUp", "qcdDown"):

    for region in sys_region_list:

        selections_regions[f"{region}_{pdf_qcd_sys}"] =  selections_regions[region]

##############

ROOT.TH1.SetDefaultSumw2()

##############
hists_models_1D = [
    (40, 0, 800, "lept1_pt", "lept1_pt"),
    (20, 0, 400, "lept2_pt", "lept2_pt"),
    (26, -2.6, 2.6, "lept1_eta", "lept1_eta"),
    (26, -2.6, 2.6, "lept2_eta", "lept2_eta"),
    (34, -3.4, 3.4, "lept1_phi", "lept1_phi"),
    (34, -3.4, 3.4, "lept2_phi", "lept2_phi"),
    (80, 0, 800, "pf_met_corr", "pf_met_corr"),
    (34, -3.4, 3.4, "pf_met_corr_phi", "pf_met_corr_phi"),
    # ak8 jet
    (24, 30.0, 160.0, "fatjet_m", "fatjet_m"),
    (80, 200.0, 2000.0, "fatjet_pt", "fatjet_pt"),
    (26, -2.6, 2.6, "fatjet_eta", "fatjet_eta"),
    (34, -3.4, 3.4, "fatjet_phi", "fatjet_phi"),
    (40, 0.0, 1.0, "fatjet_tau21", "fatjet_tau21"),
    # ak4ak4 jet
    (24, 30.0, 160.0, "dijet_m", "dijet_m"),
    (80, 0.0, 800.0, "dijet_pt", "dijet_pt"),
    (25, -5.0, 5.0, "dijet_eta", "dijet_eta"),
    (60, 0.0, 600.0, "dijet_j1_pt", "dijet_j1_pt"),
    (60, 0.0, 600.0, "dijet_j2_pt", "dijet_j2_pt"),
    (20, -2.5, 2.5, "dijet_j1_eta", "dijet_j1_eta"),
    (20, -2.5, 2.5, "dijet_j2_eta", "dijet_j2_eta"),
    # W
    (50, 0.0, 1000.0, "v_pt", "v_pt"),
    (40, -4.0, 4.0, "v_eta", "v_eta"),
    (20, 65, 105.0, "v_m", "v_m"),
    (20, 0.0, 400.0, "v_mt", "v_mt"),
    # vbf jets
    (50, 0.0, 1000.0, "vbf_j1_pt", "vbf_j1_pt"),
    (30, 0.0, 600.0, "vbf_j2_pt", "vbf_j2_pt"),
    (51, -5.1, 5.1, "vbf_j1_eta", "vbf_j1_eta"),
    (51, -5.1, 5.1, "vbf_j2_eta", "vbf_j2_eta"),
    (16, 2.0, 10.0, "vbf_jj_Deta", "vbf_jj_Deta"),
    (34, -3.4, 3.4, "vbf_j1_phi", "vbf_j1_phi"),
    (34, -3.4, 3.4, "vbf_j2_phi", "vbf_j2_phi"),
    (40, 500.0, 2500.0, "vbf_jj_m", "vbf_jj_m"),
    #
    (30, 0.0, 6.0, "boson_centrality", "boson_centrality"),
    (20, -1.0, 1.0, "zeppenfeld_w_Deta", "zeppenfeld_w_Deta"),
    (20, -1.0, 1.0, "zeppenfeld_v_Deta", "zeppenfeld_v_Deta"),
    # W V system
    (50, 0, 2500, "vv_m", "vv_m"),
    (60, 0.0, 600.0, "vv_pt", "vv_pt"),
    (20, -5.0, 5.0, "vv_eta", "vv_eta"),
    (34, -3.4, 3.4, "vv_phi", "vv_phi"),
    (40, -1.0, 1.0, "mva_score_wjj", "mva_score_wjj"),
    (40, -1.0, 1.0, "mva_score_zjj", "mva_score_zjj"),
    (40, -1.0, 1.0, "mva_score_wv", "mva_score_wv"),
    (40, -1.0, 1.0, "mva_score_zv", "mva_score_zv"),
    (np.array([-1.0, -0.3, -0.15, 0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 1]), 0, 0, "mva_score_wjj", "mva_score_wjj_var1"),
    (np.array([-1.0, -0.3, -0.15, 0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 1]), 0, 0, "mva_score_zjj", "mva_score_zjj_var1"),
    (np.array([-1.0, -0.3, -0.15, 0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 1]), 0, 0, "mva_score_wv", "mva_score_wv_var1"),
    (np.array([-1.0, -0.3, -0.15, 0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 1]), 0, 0, "mva_score_zv", "mva_score_zv_var1"),
    (1, -1.0, 1.0, "mva_score_wjj", "mva_score_wjj_1bin"),
    (1, -1.0, 1.0, "mva_score_zjj", "mva_score_zjj_1bin"),
    (1, -1.0, 1.0, "mva_score_wv", "mva_score_wv_1bin"),
    (1, -1.0, 1.0, "mva_score_zv", "mva_score_zv_1bin")
]

# for jes systematic, if needs to keep it low
hists_models_1D_SYS = []
hists_SYS_list = [
    #"mva_score_wjj_var1",
    #"mva_score_zjj_var1",
    #"mva_score_wv_var1",
    #"mva_score_zv_var1",
]
for i in hists_models_1D:
    if len(hists_SYS_list) != 0:
        if i[4] in hists_SYS_list:
            hists_models_1D_SYS.append(i)
    else:
        hists_models_1D_SYS.append(i)

# for pdf systematic, if needs to keep it low
hists_models_1D_SYS_1 = []
hists_SYS_list_1 = [
    "mva_score_wjj_var1",
    "mva_score_zjj_var1",
    "mva_score_wv_var1",
    "mva_score_zv_var1",
]
for i in hists_models_1D:
    if len(hists_SYS_list_1) != 0:
        if i[4] in hists_SYS_list_1:
            hists_models_1D_SYS_1.append(i)
    else:
        hists_models_1D_SYS_1.append(i)

# for qcd systematic, if needs to keep it low
hists_models_1D_SYS_2 = []
hists_SYS_list_2 = [
    #"mva_score_wjj_var1",
    #"mva_score_zjj_var1",
    #"mva_score_wv_var1",
    #"mva_score_zv_var1",
]
for i in hists_models_1D:
    if len(hists_SYS_list_2) != 0:
        if i[4] in hists_SYS_list_2:
            hists_models_1D_SYS_2.append(i)
    else:
        hists_models_1D_SYS_2.append(i)


histograms_dict = {}
df_samples_regions = {}

for region in args.regions:

    print(selections_regions[region])

    histograms_dict[region] = {}

    for sample_ in samples_name:

        df_samples_regions[sample_ + region] = df_samples[sample_].Filter(selections_regions[region])
        print(sample_, region)


        if "jes" in region:
            hists_models = hists_models_1D_SYS
        elif "pdf" in region:
            hists_models = hists_models_1D_SYS_1
        elif "qcd" in region:
            hists_models = hists_models_1D_SYS_2
        else:
            hists_models = hists_models_1D


        for h_ in hists_models:

            hist_name = sample_+ "_" + h_[4]
            if type(h_[0]) == np.ndarray:
                hist_model = ROOT.RDF.TH1DModel(f"{hist_name}", f"{hist_name}", len(h_[0]) - 1, h_[0])
            else:
                hist_model = ROOT.RDF.TH1DModel(f"{hist_name}", f"{hist_name}", h_[0], h_[1], h_[2])

            histograms_dict[region][hist_name] = \
                    df_samples_regions[sample_ + region].Histo1D(hist_model, h_[3], "total_weight")

            nPDF = 0
            if ("pdf" in region):
                if any(x in hist_name for x in ["VBS_EWK", "VBS_QCD"]):
                    if any(x in args.in_dir for x in ["2016", "2017", "2018"]):
                        nPDF = 103

                for i in range(nPDF):
                    histograms_dict[region][hist_name + f"_pdf_{i}"] = \
                        df_samples_regions[sample_ + region].Histo1D(hist_model, h_[3], f"total_weight_pdf_{i}")

            qcd_weight_order = []
            if ("qcd" in region):
                if any(x in hist_name for x in ["VBS_EWK", "VBS_QCD"]):
                    if ("2016" in args.in_dir):
                        qcd_weight_order = [20, 0, 5, 15, 25, 35, 40]

                    if any(x in args.in_dir for x in ["2017", "2018"]):
                        qcd_weight_order = [4, 0, 1, 3, 5, 7, 8]

                # same code, separate for just-in-case
                elif any(x in hist_name for x in ["DYJets", "WJets"]):
                    if any(x in args.in_dir for x in ["2017", "2018"]):
                        qcd_weight_order = [4, 0, 1, 3, 5, 7, 8]

                for i, j in enumerate(qcd_weight_order):
                    histograms_dict[region][hist_name + f"_qcd_{i}"] = \
                        df_samples_regions[sample_ + region].Histo1D(hist_model, h_[3], f"total_weight_qcd_{j}")


def merge_overflow_bin(hist):
    n = hist.GetNbinsX()
    hist.SetBinContent(n, hist.GetBinContent(n) + hist.GetBinContent(n + 1))


# start the event loop
progress_counter = df.Histo1D(("progress", "progress", 1, 0, 1), "evt")
progress_counter.GetValue()
print("\nLoop Completed")

ROOT.ROOT.DisableImplicitMT()


out = ROOT.TFile(args.output, "recreate")
histograms_dict_v = {}

for region in histograms_dict:

    # Get All the histograms first
    histograms_dict_v[region] = {}
    for hist_name in histograms_dict[region]:

        print(region, hist_name)
        histograms_dict_v[region][hist_name] = histograms_dict[region][hist_name].GetValue()
        merge_overflow_bin(histograms_dict_v[region][hist_name])


    t_directory = region
    for i in ("zv", "zjj", "wv", "wjj"):
        t_directory = t_directory.replace(f"_{i}", "")

    out.cd()
    out.mkdir(t_directory)
    out.cd(t_directory)

    # loop again to write, etc.
    for hist_name in histograms_dict[region]:

        # skip over intermediate hists
        if "_pdf_" in hist_name: continue
        if "_qcd_" in hist_name: continue

        if ("pdf" in region):
            if any(x in hist_name for x in ["VBS_EWK", "VBS_QCD"]):
                if ("2016" in args.in_dir) or ("2017" in args.in_dir) or ("2018" in args.in_dir):
                    nbins = histograms_dict_v[region][hist_name].GetNbinsX()
                    for bin_ in range(nbins):
                        sys_pdf = 0.0
                        # pdf weight 0, a.k.a central value peaks at 1, not equal to 1 !!
                        bin_content = histograms_dict_v[region][hist_name + "_pdf_0"].GetBinContent(bin_)
                        # first normal loop over 100 replicas
                        # https://arxiv.org/pdf/1510.03865v2.pdf
                        for i in range(1, 101):
                            diff_ = abs(histograms_dict_v[region][hist_name + f"_pdf_{i}"].GetBinContent(bin_) - bin_content)
                            sys_pdf += diff_ * diff_
                        sys_pdf = (sys_pdf) ** 0.5

                        # now alphas var index 101 (0.116), 102 (0.120)
                        bin_content_alphas_0116 = histograms_dict_v[region][hist_name + f"_pdf_101"].GetBinContent(bin_)
                        bin_content_alphas_0120 = histograms_dict_v[region][hist_name + f"_pdf_102"].GetBinContent(bin_)
                        sys_pdf_alphas = 0.5 * (0.0015 / 0.002) * (bin_content_alphas_0120 - bin_content_alphas_0116)

                        # final combined sys pdf
                        sys_pdf = ((sys_pdf)**2 + (sys_pdf_alphas)**2)**0.5


                        nominal_bin_content = histograms_dict_v[region][hist_name].GetBinContent(bin_)
                        if "Up" in region:
                            histograms_dict_v[region][hist_name].SetBinContent(bin_, nominal_bin_content + sys_pdf)
                        if "Down" in region:
                            histograms_dict_v[region][hist_name].SetBinContent(bin_, nominal_bin_content - sys_pdf)

                histograms_dict_v[region][hist_name].Write()

        elif ("qcd" in region):
            if any(x in hist_name for x in ["VBS_EWK", "VBS_QCD", "DYJets", "WJets"]):
                if ("2016" in args.in_dir) or ("2017" in args.in_dir) or ("2018" in args.in_dir):
                    nbins = histograms_dict_v[region][hist_name].GetNbinsX()
                    for bin_ in range(nbins):
                        sys_qcd = 0.0
                        # scale weight is 1 for central, so no need to use separate central hist
                        bin_content = histograms_dict_v[region][hist_name + "_qcd_0"].GetBinContent(bin_)
                        # find the largest error
                        for i in range(1, 7):
                            diff_ = abs(histograms_dict_v[region][hist_name + f"_qcd_{i}"].GetBinContent(bin_) - bin_content)
                            if diff_ > sys_qcd:
                                sys_qcd = diff_


                        nominal_bin_content = histograms_dict_v[region][hist_name].GetBinContent(bin_)
                        if "Up" in region:
                            histograms_dict_v[region][hist_name].SetBinContent(bin_, nominal_bin_content + sys_qcd)
                        if "Down" in region:
                            histograms_dict_v[region][hist_name].SetBinContent(bin_, nominal_bin_content - sys_qcd)

                histograms_dict_v[region][hist_name].Write()

        else:
            histograms_dict_v[region][hist_name].Write()

out.cd()
out.Close()

stopwatch.Print()

#ROOT.RDF.SaveGraph(df, f"{args.output.replace('.root', '.dot')}")

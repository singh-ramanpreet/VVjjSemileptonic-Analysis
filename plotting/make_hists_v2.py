#!/usr/bin/env python3

import ROOT
import argparse

parser = argparse.ArgumentParser()

parser.add_argument("--in-dir", dest="in_dir", type=str, default="../2018_May11",
                    help="region to produce hists for, default=%(default)s")

parser.add_argument("--regions", action="append", default=[],
                    help="region to produce hists for, default=%(default)s")

parser.add_argument("--output", type=str, default="hists.root",
                    help="hists output filename, default=%(default)s")

args = parser.parse_args()


ROOT.ROOT.EnableImplicitMT(4)


df = ROOT.RDataFrame("Events", f"{args.in_dir}/*.root")

samples_name = ["data_obs", "VBS_EWK", "VBS_QCD", "Top", "WJets", "DYJets_LO", "DYJets_HT", "DYJets_NLO"]

df_samples = {}
for sample_ in samples_name:
    df_samples[sample_] = df.Filter(f"sample_tag == \"{sample_}\"")


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

selections["w_mu_ch"] = selections["w_ch"] + " && " + selections["mu_ch"] + " && " + selections["mu2_ch"]
selections["w_el_ch"] = selections["w_ch"] + " && " + selections["el_ch"] + " && " + selections["el2_ch"]

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


#"boson_centrality > 0.0"
#"zeppenfeld_w_Deta < 1.0"
#"zeppenfeld_v_Deta < 1.0"

##############
### ZJJ
selections["z_common_m"] = selections["z_mu_ch"].replace("LEPT1_PT_CUT", "35").replace("LEPT2_PT_CUT", "20") \
                            + " && " + selections["vbf_jets"] \
                            + " && nBTagJet_loose == 0"

selections["z_common_e"] = selections["z_el_ch"].replace("LEPT1_PT_CUT", "40").replace("LEPT2_PT_CUT", "20") \
                            + " && " + selections["vbf_jets"] \
                            + " && nBTagJet_loose == 0"

selections_regions = {}
selections_regions["sr_zjj_m"] = selections["z_common_m"] + " && " + selections["resolved_jets"]
selections_regions["sr_zjj_e"] = selections["z_common_e"] + " && " + selections["resolved_jets"]

selections_regions["cr_vjets_zjj_m"] = selections["z_common_m"] + " && " + selections["resolved_jets_sb"]
selections_regions["cr_vjets_zjj_e"] = selections["z_common_e"] + " && " + selections["resolved_jets_sb"]

selections_regions["cr_top_zjj_m"] = selections_regions["sr_zjj_m"].replace("nBTagJet_loose == 0", "nBTagJet_loose > 0")
selections_regions["cr_top_zjj_e"] = selections_regions["sr_zjj_e"].replace("nBTagJet_loose == 0", "nBTagJet_loose > 0")

### ZV
selections_regions["sr_zv_m"] = selections["z_common_m"] + " && " + selections["boosted_jets"]
selections_regions["sr_zv_e"] = selections["z_common_e"] + " && " + selections["boosted_jets"]

selections_regions["cr_vjets_zv_m"] = selections["z_common_m"] + " && " + selections["boosted_jets_sb"]
selections_regions["cr_vjets_zv_e"] = selections["z_common_e"] + " && " + selections["boosted_jets_sb"]

selections_regions["cr_top_zv_m"] = selections_regions["sr_zv_m"].replace("nBTagJet_loose == 0", "nBTagJet_loose > 0")
selections_regions["cr_top_zv_e"] = selections_regions["sr_zv_e"].replace("nBTagJet_loose == 0", "nBTagJet_loose > 0")

##############
##############
### WJJ
selections["w_common_m"] = selections["w_mu_ch"].replace("LEPT1_PT_CUT", "35").replace("MET_CUT", "40") \
                            + " && " + selections["vbf_jets"] \
                            + " && nBTagJet_loose == 0" 

selections["w_common_e"] = selections["w_el_ch"].replace("LEPT1_PT_CUT", "40").replace("MET_CUT", "40") \
                            + " && " + selections["vbf_jets"] \
                            + " && nBTagJet_loose == 0"

selections_regions["sr_wjj_m"] = selections["w_common_m"] + " && " + selections["resolved_jets"]
selections_regions["sr_wjj_e"] = selections["w_common_e"] + " && " + selections["resolved_jets"]

selections_regions["cr_vjets_wjj_m"] = selections["w_common_m"] + " && " + selections["resolved_jets_sb"]
selections_regions["cr_vjets_wjj_e"] = selections["w_common_e"] + " && " + selections["resolved_jets_sb"]

selections_regions["cr_top_wjj_m"] = selections_regions["sr_wjj_m"].replace("nBTagJet_loose == 0", "nBTagJet_loose > 0")
selections_regions["cr_top_wjj_e"] = selections_regions["sr_wjj_e"].replace("nBTagJet_loose == 0", "nBTagJet_loose > 0")

### WV
selections_regions["sr_wv_m"] = selections["w_common_m"] + " && " + selections["resolved_jets"]
selections_regions["sr_wv_e"] = selections["w_common_e"] + " && " + selections["resolved_jets"]

selections_regions["cr_vjets_wv_m"] = selections["w_common_m"] + " && " + selections["resolved_jets_sb"]
selections_regions["cr_vjets_wv_e"] = selections["w_common_e"] + " && " + selections["resolved_jets_sb"]

selections_regions["cr_top_wv_m"] = selections_regions["sr_wv_m"].replace("nBTagJet_loose == 0", "nBTagJet_loose > 0")
selections_regions["cr_top_wv_e"] = selections_regions["sr_wv_e"].replace("nBTagJet_loose == 0", "nBTagJet_loose > 0")

##############

weight_w = "xs_weight * gen_weight * pu_weight * btag0_weight * lept1_trig_eff_weight * lept1_id_eff_weight"
weight_z =  weight_w + " * lept2_trig_eff_weight * lept2_id_eff_weight"

##############

jes_var_Z_replace = [
    "vbf_jj_m",
    "vbf_j1_pt",
    "vbf_j2_pt",
    "dijet_m",
    "dijet_pt",
    "dijet_j1_pt",
    "dijet_j2_pt",
    "fatjet_m",
    "fatjet_pt"
]

jes_var_W_replace = jes_var_Z_replace

for jes_sys in ("jesUp", "jesDown"):
    
    for region in ("sr_zjj_m", "sr_zjj_e", "sr_zv_m", "sr_zv_e"):
        
        temp_string = selections_regions[region]
        
        for jes_var in jes_var_Z_replace:
            
            temp_string = temp_string.replace(jes_var, f"{jes_var}_{jes_sys}")
    
        selections_regions[f"{region}_{jes_sys}"] =  temp_string


    for region in ("sr_wjj_m", "sr_wjj_e", "sr_wv_m", "sr_wv_e"):
        
        temp_string = selections_regions[region]
        
        for jes_var in jes_var_W_replace:
            
            temp_string = temp_string.replace(jes_var, f"{jes_var}_{jes_sys}")
    
        selections_regions[f"{region}_{jes_sys}"] =  temp_string
##############

ROOT.TH1.SetDefaultSumw2()

##############
hists_models_1D = [
    (40, 0, 800, "lept1_pt"),
    (20, 0, 400, "lept2_pt"),
    (26, -2.6, 2.6, "lept1_eta"),
    (26, -2.6, 2.6, "lept2_eta"),
    (34, -3.4, 3.4, "lept1_phi"),
    (34, -3.4, 3.4, "lept2_phi"),
    (80, 0, 800, "pf_met_corr"),
    (34, -3.4, 3.4, "pf_met_corr_phi"),
    # ak8 jet
    (24, 30.0, 160.0, "fatjet_m"),
    (80, 200.0, 2000.0, "fatjet_pt"),
    (26, -2.6, 2.6, "fatjet_eta"),
    (34, -3.4, 3.4, "fatjet_phi"),
    (40, 0.0, 1.0, "fatjet_tau21"),
    # ak4ak4 jet
    (24, 30.0, 160.0, "dijet_m"),
    (80, 0.0, 800.0, "dijet_pt"),
    (25, -5.0, 5.0, "dijet_eta"),
    (60, 0.0, 600.0, "dijet_j1_pt"),
    (60, 0.0, 600.0, "dijet_j2_pt"),
    (20, -2.5, 2.5, "dijet_j1_eta"),
    (20, -2.5, 2.5, "dijet_j2_eta"),
    # W
    (50, 0.0, 1000.0, "v_pt"),
    (40, -4.0, 4.0, "v_eta"),
    (20, 65, 105.0, "v_m"),
    (20, 0.0, 400.0, "v_mt"),
    # vbf jets
    (50, 0.0, 1000.0, "vbf_j1_pt"),
    (30, 0.0, 600.0, "vbf_j2_pt"),
    (51, -5.1, 5.1, "vbf_j1_eta"),
    (51, -5.1, 5.1, "vbf_j2_eta"),
    (16, 2.0, 10.0, "vbf_jj_Deta"),
    (34, -3.4, 3.4, "vbf_j1_phi"),
    (34, -3.4, 3.4, "vbf_j2_phi"),
    (40, 500.0, 2500.0, "vbf_jj_m"),
    #
    (30, 0.0, 6.0, "boson_centrality"),
    (20, -1.0, 1.0, "zeppenfeld_w_Deta"),
    (20, -1.0, 1.0, "zeppenfeld_v_Deta"),
    # W V system
    (50, 0, 2500, "vv_m"),
    (60, 0.0, 600.0, "vv_pt"),
    (20, -5.0, 5.0, "vv_eta"),
    (34, -3.4, 3.4, "vv_phi"),
    (40, -1.0, 1.0, "mva_score_wjj"),
    (40, -1.0, 1.0, "mva_score_zjj"),
    (40, -1.0, 1.0, "mva_score_wv"),
    (40, -1.0, 1.0, "mva_score_zv")
]

hists_models_1D_jesUp = [
    (40, -1.0, 1.0, "mva_score_wjj_jesUp"),
    (40, -1.0, 1.0, "mva_score_zjj_jesUp"),
    (40, -1.0, 1.0, "mva_score_wv_jesUp"),
    (40, -1.0, 1.0, "mva_score_zv_jesUp")
]

hists_models_1D_jesDown = [
    (40, -1.0, 1.0, "mva_score_wjj_jesDown"),
    (40, -1.0, 1.0, "mva_score_zjj_jesDown"),
    (40, -1.0, 1.0, "mva_score_wv_jesDown"),
    (40, -1.0, 1.0, "mva_score_zv_jesDown")
]


histograms_dict = {}
df_samples_regions = {}

for region in args.regions:

    print (selections_regions[region])

    histograms_dict[region] = {}

    for sample_ in samples_name:

        df_samples_regions[sample_ + region] = df_samples[sample_].Filter(selections_regions[region])
        print(sample_, region)

        if ("zv" in region) or ("zjj" in region):
            weight = weight_z
        else:
            weight = weight_w
        print("Weight -> ", weight)


        if "jesUp" in region:
            hists_models = hists_models_1D_jesUp
        elif "jesDown" in region:
            hists_models = hists_models_1D_jesDown
        else:
            hists_models = hists_models_1D
        
        
        for h_ in hists_models:
            
            hist_name = sample_+ "_" + h_[3]
            hist_model = ROOT.RDF.TH1DModel(f"{hist_name}", f"{hist_name}", h_[0], h_[1], h_[2])               
            histograms_dict[region][hist_name] = \
                    df_samples_regions[sample_ + region].Define("total_weight", weight).Histo1D(hist_model, h_[3], "total_weight")


def merge_overflow_bin(hist):
    n = hist.GetNbinsX()
    hist.SetBinContent(n, hist.GetBinContent(n) + hist.GetBinContent(n + 1))

out = ROOT.TFile(args.output, "recreate")
histograms_dict_v = {}

for region in histograms_dict:

    out.mkdir(region)
    out.cd(region)
    print(region)

    histograms_dict_v[region] = {}
    for hist_name in histograms_dict[region]:
        
        print(hist_name)
        histograms_dict_v[region][hist_name] = histograms_dict[region][hist_name].GetValue()
        merge_overflow_bin(histograms_dict_v[region][hist_name])
        histograms_dict_v[region][hist_name].Write()

out.cd()
out.Close()

ROOT.RDF.SaveGraph(df, f"{args.output.replace('.root', '.dot')}")

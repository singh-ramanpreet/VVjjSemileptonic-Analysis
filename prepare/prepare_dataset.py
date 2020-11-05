#!/usr/bin/env python3

import argparse
import os
import json
import ROOT

from collections import OrderedDict
from pprint import pprint

ROOT.PyConfig.IgnoreCommandLineOptions = True

parser = argparse.ArgumentParser()

parser.add_argument("--datasets", type=str, default="../datasets_2016.json",
                    help="json file: info of datasets, default=%(default)s")

parser.add_argument("--sample-tag", dest="sample_tag", type=str, default="all",
                    help="sample tag to process from json file, default=%(default)s")

parser.add_argument("--sample-number", dest="sample_number", type=str, default="all",
                    help="sample number in filelist of sample tag to process, default=%(default)s")

parser.add_argument("--year", type=str, default="2016",
                    help="dataset year, default=%(default)s")

parser.add_argument("--variables", type=str, default="../variables_map.json",
                    help="json file: variables central and systematic map, default=%(default)s")

parser.add_argument("--mva-name", dest="mva_name", action="append",
                    help="name of mva: wjj, wv, zjj, zv, default=%(default)s")

parser.add_argument("--mva-xml", dest="mva_xml", action="append",
                    help="mva training weight file (xml), default=%(default)s")

parser.add_argument("--mva-var-list", dest="mva_var_list", action="append",
                    help="mva training variable list, default=%(default)s")

parser.add_argument("--output", type=str, default="2016",
                    help="output directory, default=%(default)s")

args = parser.parse_args()

# variables map
variables_map = OrderedDict(json.load(open(args.variables, "r")))
pprint(variables_map, width=120)

# make TMVA readers in ROOT c++ namespace
if args.mva_name != None:

    evaluate_mva_var_list = {i: {} for i in args.mva_name}

    for mva_name, mva_xml, mva_var_list in zip(args.mva_name, args.mva_xml, args.mva_var_list):

        print(f"MVA: {mva_name} --> training file: {mva_xml} --> variables list: {mva_var_list}")

        mva_variables = open(mva_var_list).readlines()
        mva_variables = [i.rstrip("\n") for i in mva_variables]

        ROOT.gInterpreter.ProcessLine(f"TMVA::Reader mva_reader_{mva_name};")
        for var in mva_variables:
             ROOT.gInterpreter.ProcessLine(f"""
             Float_t {var}_{mva_name};
             mva_reader_{mva_name}.AddVariable("{var}", &{var}_{mva_name});
             """)
        ROOT.gInterpreter.ProcessLine(f"""
        mva_reader_{mva_name}.BookMVA("BDT", "{mva_xml}")
        """)

        # central
        evaluate_mva_var_list[mva_name]["central"] = f"std::vector<Double_t>{{{','.join(mva_variables)}}}"
        # jesUp, jesDown
        systematics = ("jesUp", "jesDown")
        for systematic in systematics:
            var_list_ = []
            for var in mva_variables:
                if var == "v_m" and (mva_name == "zjj" or mva_name == "zv"):
                    var_list_.append(var)
                elif var + "_" + systematic in variables_map:
                    var_list_.append(var + "_" + systematic)
                else:
                    var_list_.append(var)

            evaluate_mva_var_list[mva_name][systematic] = f"std::vector<Double_t>{{{','.join(var_list_)}}}"

        print("=========================================")
        print(f"MVA {mva_name} will be evaluated with: ")
        print("central: -->")
        print(evaluate_mva_var_list[mva_name]["central"])
        for systematic in systematics:
            print(f"{systematic}: -->")
            print(evaluate_mva_var_list[mva_name][systematic])
        print("=========================================")

#input("....")

# Loop over samples
samples_dict = json.load(open(args.datasets, "r"))

for key in samples_dict:

    if args.sample_tag != "all" and args.sample_tag != key: continue

    location = samples_dict[key]["location"]
    filelist = samples_dict[key]["filelist"]
    lumi = samples_dict[key]["lumi"]

    for i, sample in enumerate(filelist):

        if args.sample_number != "all" and args.sample_number != str(i): continue

        root_file = location + sample["name"]
        xs = sample["xs"]
        nMC = 0
        nMCneg = 0
        kf = 1.0

        if "nMC" in sample.keys(): nMC = sample["nMC"]
        if "nMCneg" in sample.keys(): nMCneg = sample["nMCneg"]
        if "kf" in sample.keys(): kf = sample["kf"]

        if nMC == 0:
            file_ = ROOT.TFile.Open(root_file)
            total_events_hist = file_.Get("TotalEvents")
            nMCneg = total_events_hist.GetBinContent(1)
            nMC = total_events_hist.GetBinContent(2)
            print(nMC, nMCneg)

        xs_weight = (lumi * xs * kf) / (nMC - (2 * nMCneg))

        print("=========================================")
        print("loading ... ", key, sample["name"])

        # Disable MT because TMVA Evaluation is not thread-safe
        ROOT.ROOT.DisableImplicitMT()

        df = ROOT.RDataFrame("Events", root_file)
        variables_out = ROOT.std.vector("string")()
        count = df.Count()
        total_entries = count.GetValue()

        # keep all branches in input tree
        column_list = list(df.GetColumnNames())
        column_dict = OrderedDict(zip(column_list, column_list))
        column_dict.update(variables_map)
        variables_map = column_dict.copy()

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

        # making it sure for data
        # will set them equal to 1.0f
        weights_map_DATA = [
             "btag0_weight",
             "gen_weight",
             "pu_weight",
             "pu_weight_PUUp",
             "pu_weight_PUDown",
             "lept1_trig_eff_weight",
             "lept2_trig_eff_weight",
             "lept1_id_eff_weight",
             "lept2_id_eff_weight",
             "L1PFWeight",
        ]

        for new_name, var_name in variables_map.items():
            variables_out.push_back(new_name)
            if new_name != var_name:
                if new_name in weights_map_DATA and "data" in key:
                    print(f"Setting <== {new_name} ==> equal to 1.0f for DATA")
                    df = df.Define(new_name, "1.0f")
                else:
                    df = df.Define(new_name, var_name)

        if args.mva_name != None:
            for mva_ in args.mva_name:
                for sys in ("central", "jesUp", "jesDown"):
                    mva_value = f"mva_reader_{mva_}.EvaluateMVA({evaluate_mva_var_list[mva_][sys]}, \"BDT\")"
                    if sys == "central":
                        mva_out_name = f"mva_score_{mva_}"
                    else:
                        mva_out_name = f"mva_score_{mva_}_{sys}"
                    print(f"MVA {mva_} {sys} value is stored in: {mva_out_name}, calculated using {mva_value.split('.')[0]}")

                    df = df.Define(mva_out_name, mva_value)
                    variables_out.push_back(mva_out_name)

        df = df.Define("sample_tag", "return std::string(\""+key+"\");")
        variables_out.push_back("sample_tag")

        df = df.Define("xs_weight", str(xs_weight))
        variables_out.push_back("xs_weight")

        os.makedirs(args.output, exist_ok=True)
        output_filename = f"{args.output}/{sample['name']}"
        df.Snapshot("Events", output_filename, variables_out)
        print("\n")

print("DONE")

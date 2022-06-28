#!/usr/bin/env python3

import ROOT
import numpy as np
ROOT.gROOT.SetBatch()
ROOT.PyConfig.IgnoreCommandLineOptions = True
import os
import argparse

parser = argparse.ArgumentParser()

parser.add_argument("-f", type=str, default="test.root")
parser.add_argument("-o", type=int, default=0)

args = parser.parse_args()

root_file = ROOT.TFile.Open(args.f)

list_of_keys = root_file.GetListOfKeys()

for i in list_of_keys:
    #if all(j != i.GetName().rstrip() for j in ["sr1_l"]): continue
    tdir = root_file.Get(i.GetName())
    if tdir.ClassName() != "TDirectoryFile": continue
    print(tdir.GetName())

    if args.o == 0:
        h_data_yield = tdir.Get("data_obs_v_lep_pt")
        h_vbs_ewk = tdir.Get('VBS_EWK_v_lep_pt')
        h_vbs_qcd = tdir.Get('VBS_QCD_v_lep_pt')
        h_top = tdir.Get('Top_v_lep_pt')
        h_dyjets = tdir.Get('DYJets_HT_v_lep_pt')

        if type(h_data_yield) == ROOT.TObject: continue
        Zpt_bins = [0,80,160,240,320,400,480]
        sf_str = ""
        for i in range(len(Zpt_bins)):
            first_bin = h_data_yield.FindBin(Zpt_bins[i] - 0.01)
            if i != len(Zpt_bins) - 1:
                second_bin = h_data_yield.FindBin(Zpt_bins[i + 1] - 0.01)
            else:
                second_bin = h_data_yield.GetNbinsX()

            if first_bin == second_bin: break

            data_yield = h_data_yield.Integral(first_bin, second_bin)
            vbs_ewk_yield = h_vbs_ewk.Integral(first_bin, second_bin)
            vbs_qcd_yield = h_vbs_qcd.Integral(first_bin, second_bin)
            top_yield = h_top.Integral(first_bin, second_bin)
            dyjets_yield = h_dyjets.Integral(first_bin, second_bin)

            bkg_yield = vbs_qcd_yield + top_yield + dyjets_yield
            dyjets_sf = (data_yield - top_yield - vbs_qcd_yield)/dyjets_yield

            print(f"bin: {i}, data:{data_yield}, bkg:{bkg_yield}, bkg_scaled:{dyjets_sf*dyjets_yield + top_yield + vbs_qcd_yield}")

            if i != len(Zpt_bins) - 1:
                sf_str_ = f"dilep_pt > {Zpt_bins[i]} && dilep_pt < {Zpt_bins[i + 1]} ? {dyjets_sf:.2f} \" \\\n \": "
            else:
                sf_str_ = f"dilep_pt > {Zpt_bins[i]} ? {dyjets_sf:.2f} \" \\\n \": "
            if i == 0:
                sf_str = sf_str_
            else:
                sf_str += sf_str_

    if args.o == 1:
        h_data_yield = tdir.Get("data_obs_v_lep_pt_vbf_j2_pt")
        h_vbs_ewk = tdir.Get('VBS_EWK_v_lep_pt_vbf_j2_pt')
        h_vbs_qcd = tdir.Get('VBS_QCD_v_lep_pt_vbf_j2_pt')
        h_top = tdir.Get('Top_v_lep_pt_vbf_j2_pt')
        h_dyjets = tdir.Get('DYJets_HT_v_lep_pt_vbf_j2_pt')

        if type(h_data_yield) == ROOT.TObject: continue

        Zpt_bins = [0,80,160,240,320,400]
        vbf_j2_pt_bins = [30,50,100,150,250]
        histo = ROOT.TH2D("dyjets_sf", "dyjets_sf;Zpt;VBS j2 pt",
                          len(Zpt_bins) - 1, np.array(Zpt_bins, dtype=np.float64),
                          len(vbf_j2_pt_bins) - 1, np.array(vbf_j2_pt_bins, dtype=np.float64) )
        histo_out = ROOT.TFile.Open(tdir.GetName() + "_sf_from_" + args.f, "recreate")
        
        sf_str = ""
        for i in range(len(Zpt_bins)):
            for j in range(len(vbf_j2_pt_bins)):
                first_bin_x = h_data_yield.GetXaxis().FindBin(Zpt_bins[i] - 0.01)
                first_bin_y = h_data_yield.GetYaxis().FindBin(vbf_j2_pt_bins[j] - 0.01)
                if i != len(Zpt_bins) - 1:
                    second_bin_x = h_data_yield.GetXaxis().FindBin(Zpt_bins[i + 1] - 0.01)
                else:
                    second_bin_x = h_data_yield.GetNbinsX()

                if j != len(vbf_j2_pt_bins) - 1:
                    second_bin_y = h_data_yield.GetYaxis().FindBin(vbf_j2_pt_bins[j + 1] - 0.01)
                else:
                    second_bin_y = h_data_yield.GetNbinsY()

                if first_bin_x == second_bin_x: break
                if first_bin_y == second_bin_y: break

                data_yield = h_data_yield.Integral(first_bin_x, second_bin_x, first_bin_y, second_bin_y)
                vbs_ewk_yield = h_vbs_ewk.Integral(first_bin_x, second_bin_x, first_bin_y, second_bin_y)
                vbs_qcd_yield = h_vbs_qcd.Integral(first_bin_x, second_bin_x, first_bin_y, second_bin_y)
                top_yield = h_top.Integral(first_bin_x, second_bin_x, first_bin_y, second_bin_y)
                dyjets_yield = h_dyjets.Integral(first_bin_x, second_bin_x, first_bin_y, second_bin_y)

                bkg_yield = vbs_qcd_yield + top_yield + dyjets_yield
                dyjets_sf = (data_yield - top_yield - vbs_qcd_yield)/dyjets_yield
                histo.SetBinContent(i + 1, j + 1, dyjets_sf)

                #print(f"bin_x: {i}, bin_y: {j}, data:{data_yield}, bkg:{bkg_yield}, bkg_scaled:{dyjets_sf*dyjets_yield + top_yield + vbs_qcd_yield}")

                if i != len(Zpt_bins) - 1:
                    sf_str_ = f"dilep_pt > {Zpt_bins[i]} && dilep_pt < {Zpt_bins[i + 1]} && "
                else:
                    sf_str_ = f"dilep_pt > {Zpt_bins[i]} && "
                if j != len(vbf_j2_pt_bins) - 1:
                    sf_str2_ = f"vbf2_AK4_pt > {vbf_j2_pt_bins[j]} && vbf2_AK4_pt < {vbf_j2_pt_bins[j + 1]} ? {dyjets_sf:.2f} \" \\\n \": "
                else:
                    sf_str2_ = f"vbf2_AK4_pt > {vbf_j2_pt_bins[j]} ? {dyjets_sf:.2f} \" \\\n \": "
                if i == 0 and j == 0:
                    sf_str = sf_str_ + sf_str2_
                else:
                    sf_str += sf_str_ + sf_str2_
        histo.Write()
        histo_out.Write()
        del histo
        del histo_out
    print(sf_str)
#!/bin/bash

./make_mc_data_hists.py --region no_cut --lepton m
./make_mc_data_hists.py --region no_cut --lepton e

./make_mc_data_hists.py --region l_pt1_cut --lepton m
./make_mc_data_hists.py --region l_pt1_cut --lepton e

./make_mc_data_hists.py --region signal_loose_W --lepton m
./make_mc_data_hists.py --region signal_loose_W --lepton e

./make_mc_data_hists.py --region signal_tight_W --lepton m
./make_mc_data_hists.py --region signal_tight_W --lepton e

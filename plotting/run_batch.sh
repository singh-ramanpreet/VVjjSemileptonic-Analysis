#!/bin/bash

run_list=("signal_tight_W")
run_list+=("signal_tight_01_W" "signal_tight_02_W" "signal_tight_03_W" "signal_tight_04_W" "signal_tight_05_W")

for region in ${run_list[*]}; do
    echo ${region}
    ./make_mc_data_hists.py --region ${region} --lepton m
    ./make_mc_data_hists.py --region ${region} --lepton e
    hadd ${region}.root ${region}_m.root ${region}_e.root
done

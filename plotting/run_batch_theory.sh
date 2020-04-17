#!/bin/bash
export PYTHONUNBUFFERED=true

boson="W"
year="2016"
region_list=("train_wjj_01" "train_wv_01")

for region in "train_wjj_01" "train_wv_01";
do
    if [[ $region == "train_wjj_01" ]];
    then
        mva_folder="wjj_BDTG6"
    fi
    if [[ $region == "train_wv_01" ]];
    then
        mva_folder="wv_BDTG6"
    fi
    ./pdf_qcd_systematics.py \
    --datasets ../datasets_${year}.json \
    --mva ${mva_folder}/weights/VBS_BDT.weights.xml \
    --mva-var-list ${mva_folder}/variable_list.txt \
    --lepton e --boson ${boson} --region ${region}

    ./pdf_qcd_systematics.py \
    --datasets ../datasets_${year}.json \
    --mva ${mva_folder}/weights/VBS_BDT.weights.xml \
    --mva-var-list ${mva_folder}/variable_list.txt \
    --lepton m --boson ${boson} --region ${region}

    hadd -f ${region}_${year}_theoryUnc.root ${region}_theoryUnc_e.root ${region}_theoryUnc_m.root
    rm ${region}_theoryUnc_m.root
    rm ${region}_theoryUnc_e.root
done

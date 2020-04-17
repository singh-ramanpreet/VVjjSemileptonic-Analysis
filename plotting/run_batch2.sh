#!/bin/bash
export PYTHONUNBUFFERED=true

#mva="wv_BDTG6"
mva="wjj_BDTG6"
boson="W"
year="2018"
#region_list=("cr_wjets_wv_02" "cr_top_wv_02" "train_wv_02")
region_list=("cr_wjets_wjj_02" "cr_top_wjj_02" "train_wjj_02")
#region_list=("cr_wjets_wv_01" "cr_top_wv_01" "train_wv_01")
#region_list=("cr_wjets_wjj_01" "cr_top_wjj_01" "train_wjj_01")
#region_list=("train_wv_01")

for region in "${region_list[@]}";
do
    systematics=("")

    if [[ "${region}" == "train"* ]];
    then
        systematics=("" "jesUp" "jesDown")
    fi

    for sys in "${systematics[@]}";
    do
        if [[ ${sys} == "" ]];
        then
            fileTag=${mva}
        else
            fileTag=${sys}_${mva}
        fi

       ./make_hists.py --dframes df_dataset_${year}_${fileTag}.awkd --lepton e --boson ${boson} --region ${region} --info_out ${fileTag}
       ./make_hists.py --dframes df_dataset_${year}_${fileTag}.awkd --lepton m --boson ${boson} --region ${region} --info_out ${fileTag}

        hadd -f ${region}_${fileTag}.root ${region}_${fileTag}_e.root ${region}_${fileTag}_m.root

        rootmkdir -p ${region}_${mva}_${year}.root:${sys}/_e/
        rootmkdir -p ${region}_${mva}_${year}.root:${sys}/_m/

        rootcp ${region}_${fileTag}.root:* ${region}_${mva}_${year}.root:${sys}/
        rootcp ${region}_${fileTag}_e.root:* ${region}_${mva}_${year}.root:${sys}/_e/
        rootcp ${region}_${fileTag}_m.root:* ${region}_${mva}_${year}.root:${sys}/_m/

        rm ${region}_${fileTag}.root
        rm ${region}_${fileTag}_e.root
        rm ${region}_${fileTag}_m.root
    done
done

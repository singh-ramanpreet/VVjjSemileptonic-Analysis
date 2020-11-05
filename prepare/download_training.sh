#!/bin/bash

mkdir -p trainings

wv_ver="wv_BDTG81"
xrdcp root://cmseos.fnal.gov//store/user/rsingh/wv_vbs_ntuples/training_out/${wv_ver}/weights/VBS_BDT.weights.xml ./trainings/wv_weights.xml
xrdcp root://cmseos.fnal.gov//store/user/rsingh/wv_vbs_ntuples/training_out/${wv_ver}/variable_list.txt ./trainings/wv_variable_list.txt

wjj_ver="wjj_BDTG81"
xrdcp root://cmseos.fnal.gov//store/user/rsingh/wv_vbs_ntuples/training_out/${wjj_ver}/weights/VBS_BDT.weights.xml ./trainings/wjj_weights.xml
xrdcp root://cmseos.fnal.gov//store/user/rsingh/wv_vbs_ntuples/training_out/${wjj_ver}/variable_list.txt ./trainings/wjj_variable_list.txt

zv_ver="zv_BDTG3"
xrdcp root://cmseos.fnal.gov//store/user/rsingh/wv_vbs_ntuples/training_out/${zv_ver}/weights/VBS_BDT.weights.xml ./trainings/zv_weights.xml
xrdcp root://cmseos.fnal.gov//store/user/rsingh/wv_vbs_ntuples/training_out/${zv_ver}/variable_list.txt ./trainings/zv_variable_list.txt

zjj_ver="zjj_BDTG3"
xrdcp root://cmseos.fnal.gov//store/user/rsingh/wv_vbs_ntuples/training_out/${zjj_ver}/weights/VBS_BDT.weights.xml ./trainings/zjj_weights.xml
xrdcp root://cmseos.fnal.gov//store/user/rsingh/wv_vbs_ntuples/training_out/${zjj_ver}/variable_list.txt ./trainings/zjj_variable_list.txt

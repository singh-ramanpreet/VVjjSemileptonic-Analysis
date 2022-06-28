#!/bin/bash

prepare_step_files_dir=${1} #should contain sub-directories with years
training_input_dir_location=${2}

file_list_patterns=(".*ZTo2L.*dipoleRecoil.*" "^DYJets.*_HT.*")

for year in 2016 2017 2018; do
  for pattern in ${file_list_patterns[@]}; do
    for file in $(eos ls ${prepare_step_files_dir}/${year} | grep -E ${pattern}); do
      filename=$(basename ${file})
      # eos ln <name of the symbolic to be created> <target file or folder>
      eos ln ${training_input_dir_location}/${year}_${filename} ${prepare_step_files_dir}/${year}/${file}
    done
  done
done
exit

#!/bin/bash

hists_dir="hists_output"
out_dir="current"
output_tag="2021-05-12_binfix"
tar_file=${output_tag}.tar.gz

#run_on_years=("2016")
run_on_years=("2016" "2017" "2018")

run_on_channels=("zv" "zjj")

run_rootcp=true
if [[ -f ${out_dir}/${tar_file} ]]
then
  echo "this script was run before, existing root files:"
  ls -1 ${out_dir}/${output_tag}*.root
  read -r -p "Do you want to overwrite them? [y/N] " response
  response=${response,,}
  if [[ "$response" =~ ^(yes|y)$ ]]
  then
    echo "=> Removing"
    rm -v ${out_dir}/${output_tag}*.root
  else
    echo "=> Skipping"
    run_rootcp=false
  fi
fi

for channel in ${run_on_channels[*]}
do
  for year in ${run_on_years[*]}
  do
  outTag=${output_tag}_${year}
  out_filename=${out_dir}/${output_tag}_${year}_${channel}.root

  if $run_rootcp
  then
    echo "=> Merging in ${out_filename}"
    rootcp -r ${hists_dir}/hists_${output_tag}_${year}*${channel}*.root ${out_filename}
  fi
  done

  cp ${hists_dir}/${tar_file} ${out_dir}/${tar_file}
  tar -zcf ${out_dir}/${tar_file/.tar.gz/_log.tar.gz} \
    -P -T <(\ls -1 ${ANALYSIS_BASE}/plotting/condor_logs/hists_${tar_file/.tar.gz/}_*)

done

exit

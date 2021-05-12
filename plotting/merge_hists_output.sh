#!/bin/bash

hists_dir="hists_output"
out_dir="current"
output_tag="2021-05-12-binfix"
tar_file=${output_tag}.tar.gz

#run_on_years=("2016")
run_on_years=("2016" "2017" "2018")

run_on_channels=("zv" "zjj")

for channel in ${run_on_channels[*]}
do
  for year in ${run_on_years[*]}
  do
  outTag=${output_tag}_${year}
  out_filename=${out_dir}/${output_tag}_${year}_${channel}.root

  run_rootcp=true
  if [[ -f ${out_filename} ]]
  then
    echo "${out_filename} already exists."
    read -r -p "Do you want to overwrite ${out_filename}? [y/N] " response
    response=${response,,}
    if [[ "$response" =~ ^(yes|y)$ ]]
    then
      echo "=> Removing ${out_filename}"
      rm ${out_filename}
    else
      echo "=> Skipping ${out_filename}"
      run_rootcp=false
    fi
  fi
  $run_rootcp && echo "=> Merging in ${out_filename}"
  $run_rootcp && rootcp -r ${hists_dir}/hists_${output_tag}_${year}*${channel}*.root ${out_filename}

  done
done

exit

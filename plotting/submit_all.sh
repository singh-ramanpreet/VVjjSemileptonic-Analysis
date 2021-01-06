#!/bin/bash

dateTag=${1}
waitTime=${2:-600}
waitTimeFileCount=${3:-600}

for year in 2016 2017 2018
do
  outputTag=${year}_${dateTag}
  printf '%s\n' \
  'year='${year} \
  'outputTag'=${outputTag} \
  'waitTime'=${waitTime} \
  'waitTimeFileCount='${waitTimeFileCount} \
  'eos_prepared_path=/eos/uscms/store/user/singhr/wv_vbs_ntuples/mva_z11_2020_Dec_12' \
  '' \
  '# expected number of root files' \
  'if [[ "$year" == "2016" ]]' \
  'then' \
  '  expectedFiles=103' \
  'elif [[ "$year" == "2017" ]]' \
  'then' \
  '  expectedFiles=176' \
  'elif [[ "$year" == "2018" ]]' \
  'then' \
  '  expectedFiles=189' \
  'fi' \
  '' \
  'actualFiles=$(eos root://cmseos.fnal.gov ls ${eos_prepared_path}/${year}/ | grep ".root" | wc -l)' \
  '' \
  'while [[ ${expectedFiles} != ${actualFiles} ]]' \
  'do' \
  '  actualFiles=$(eos root://cmseos.fnal.gov ls ${eos_prepared_path}/${year}/ | grep ".root" | wc -l)' \
  '  echo "Prepare step still running"' \
  '  echo "Currently done $actualFiles out of $expectedFiles"' \
  '  sleep ${waitTimeFileCount}' \
  'done' \
  '' \
  '#final wait, since ls can see file when it is being copied to eos.' \
  'sleep ${waitTime}' \
  '' \
  'condor_submit base_dir=root://cmseos.fnal.gov/${eos_prepared_path} in_dir=${year} outTag=${outputTag} channel=zv year=${year} submit_make_hists.jdl' \
  'condor_submit base_dir=root://cmseos.fnal.gov/${eos_prepared_path} in_dir=${year} outTag=${outputTag} channel=zjj year=${year} submit_make_hists.jdl' \
  '#echo condor_submit base_dir=${eos_prepared_path} in_dir=${year} outTag=${outputTag} channel=wv year=${year} submit_make_hists.jdl' \
  '#echo condor_submit base_dir=${eos_prepared_path} in_dir=${year} outTag=${outputTag} channel=wjj year=${year} submit_make_hists.jdl' \
  '' | nohup bash &
done

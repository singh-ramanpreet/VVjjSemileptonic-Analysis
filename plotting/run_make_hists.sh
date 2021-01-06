#!/bin/bash
export PYTHONUNBUFFERED=true
# ./run_make_hists.sh {local, .tar.gz file} <region> <year> <base-dir> <in-dir> <threads> <hist out name>

tar_file=${1}
region=${2//./ --regions }
year=${3}
base_dir=${4}
in_dir=${5}
threads=${6}
output=${7}

if [[ ${tar_file} == *".tar.gz" ]]
then
  mkdir -p Analysis
  tar -xzf setup.tar.gz --strip 1 --directory Analysis
  cd Analysis
  source setup/setup.sh
  cd plotting
fi

./make_hists.py \
  --base-dir ${base_dir} \
  --in-dir ${in_dir} \
  --year ${year} \
  --regions ${region} \
  --output ${output} \
  --threads ${threads}

if [[ ${tar_file} == *".tar.gz" ]]
then
  mv -vf ${output} ../../${output}
  cd ../../
  rm -vf *docker*
fi

#!/bin/bash
# ./run_prepare.sh {local, condor} <year> <output-folder> <sample-name> <eos-location> <is-without-mva>

tar_file=${1}
year=${2}
output=${3}
sampleName=${4}
eosPath=${5}
isWithoutMVA=${6:-No}

if [[ ${tar_file} == *".tar.gz" ]]
then
  mkdir -p Analysis
  tar -xzf ${tar_file} --strip 1 --directory Analysis
  cd Analysis
  source setup/setup.sh
  cd prepare
fi

if [[ "${isWithoutMVA}" == "No" ]]
then
  echo "Running with MVA evaluation"
  python3 -u prepare_dataset.py \
    --datasets ../datasets_${year}.json \
    --sample-name ${sampleName} \
    --year ${year} \
    --output ${output} \
    --mva-name zv \
    --mva-xml trainings/zv_weights.xml \
    --mva-var-list trainings/zv_variable_list.txt \
    --mva-name zjj \
    --mva-xml trainings/zjj_weights.xml \
    --mva-var-list trainings/zjj_variable_list.txt \
    --mva-name wv \
    --mva-xml trainings/wv_weights.xml \
    --mva-var-list trainings/wv_variable_list.txt \
    --mva-name wjj \
    --mva-xml trainings/wjj_weights.xml \
    --mva-var-list trainings/wjj_variable_list.txt

else
  echo "Running without MVA"
  python3 -u prepare_dataset.py \
    --datasets ../datasets_${year}.json \
    --sample-name ${sampleName} \
    --year ${year} \
    --output ${output}
fi


if [[ ${tar_file} == *".tar.gz" ]]
then
  ls -al
  xrdcp -rpf ${output} ${eosPath}/$(dirname ${output})/
  rm -rvf ${output}
  cd ../../
  ls -al
  rm -vf *docker*
fi

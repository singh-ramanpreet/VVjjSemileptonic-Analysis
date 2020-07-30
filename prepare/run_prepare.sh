#!/bin/bash
# ./run_prepare.sh {local, condor} <year> <output-folder> <sample-tag-string>

if [[ ${1} == "condor" ]]; then
    tar -xzf setup.tar.gz
    cd WVAnalysis
    source setup_env/setup.sh
    cd prepare
fi

year=${2}
output=${3}
sampleTag=${4}
sampleNumber=${5}
logFile=${year}_${sampleTag}_prepare.log

python3 -u prepare_dataset.py \
--datasets ../datasets_${year}.json \
--sample-tag ${sampleTag} \
--sample-number ${sampleNumber} \
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

if [[ ${1} == "condor" ]]; then
    ls -al
    xrdcp -rpf ${output} root://cmseos.fnal.gov//store/user/rsingh/wv_vbs_ntuples/$(dirname ${output})/
    rm -rvf ${output}
    cd ../../
    ls -al
    rm -vf *docker*
fi

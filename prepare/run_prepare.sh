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
--mva-xml zv_BDTG1/weights/VBS_BDT.weights.xml \
--mva-var-list zv_BDTG1/variable_list.txt \
--mva-name zjj \
--mva-xml zjj_BDTG1/weights/VBS_BDT.weights.xml \
--mva-var-list zjj_BDTG1/variable_list.txt \
--mva-name wv \
--mva-xml wv_BDTG6/weights/VBS_BDT.weights.xml \
--mva-var-list wv_BDTG6/variable_list.txt \
--mva-name wjj \
--mva-xml wjj_BDTG6/weights/VBS_BDT.weights.xml \
--mva-var-list wjj_BDTG6/variable_list.txt

if [[ ${1} == "condor" ]]; then
    ls -al
    xrdcp -rf ${output} root://cmseos.fnal.gov//store/user/rsingh/
    rm -rvf ${output}
    cd ../../
    ls -al
    rm -vf *docker*
fi

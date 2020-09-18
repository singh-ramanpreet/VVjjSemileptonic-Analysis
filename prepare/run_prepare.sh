#!/bin/bash
# ./run_prepare.sh {local, condor} <year> <output-folder> <sample-tag-string> <sample number> <eos-location> [--without-mva]

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
eosPath=${6}
isWithoutMVA=${7:-No}


if [[ "${isWithoutMVA}" == "No" ]]; then

    echo "Running with MVA evaluation"

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

else

    echo "Running without MVA"

    python3 -u prepare_dataset.py \
        --datasets ../datasets_${year}.json \
        --sample-tag ${sampleTag} \
        --sample-number ${sampleNumber} \
        --year ${year} \
        --output ${output}

fi


if [[ ${1} == "condor" ]]; then
    ls -al
    xrdcp -rpf ${output} ${eosPath}/$(dirname ${output})/
    rm -rvf ${output}
    cd ../../
    ls -al
    rm -vf *docker*
fi

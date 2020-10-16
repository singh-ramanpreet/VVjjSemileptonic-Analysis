#!/bin/bash
export PYTHONUNBUFFERED=true
# ./run_make_hists.sh {local, condor} <region> <base-dir> <in-dir> <threads> <hist out name>

if [[ ${1} == "condor" ]]; then
    tar -xzf setup.tar.gz
    cd WVAnalysis
    source setup_env/setup.sh
    cd plotting
fi

region=${2//_plus_/ --regions }
base_dir=${3}
in_dir=${4}
threads=${5}
output=${6}

./make_hists.py \
    --base-dir ${base_dir} \
    --in-dir ${in_dir} \
    --regions ${region} \
    --output ${output} \
    --threads ${threads}

if [[ ${1} == "condor" ]]; then
    ls -al
    mv -vf ${output} ../../${output}
    cd ../../
    ls -al
    rm -vf *docker*
fi

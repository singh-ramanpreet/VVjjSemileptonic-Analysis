#!/bin/bash
export PYTHONUNBUFFERED=true
# ./run_make_hists.sh {local, condor} <region> <in-dir> <threads> <hist out name>

if [[ ${1} == "condor" ]]; then
    tar -xzf setup.tar.gz
    cd WVAnalysis
    source setup_env/setup.sh
    cd plotting
fi

region=${2}
in_dir=${3}
threads=${4}
output=${5}

./make_hists.py \
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

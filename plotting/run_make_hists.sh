#!/bin/bash
export PYTHONUNBUFFERED=true
# ./run_make_hists.sh {local, condor} <channel> <in-dir> <threads> <hist out name>

if [[ ${1} == "condor" ]]; then
    tar -xzf setup.tar.gz
    cd WVAnalysis
    source setup_env/setup.sh
    cd plotting
fi

channel=${2}
in_dir=${3}
threads=${4}
output=${5}

./make_hists.py \
--in-dir ${in_dir} \
--regions sr_${channel}_m \
--regions sr_${channel}_m_jesUp \
--regions sr_${channel}_m_jesDown \
--regions sr_${channel}_e \
--regions sr_${channel}_e_jesUp \
--regions sr_${channel}_e_jesDown \
--regions cr_vjets_${channel}_m \
--regions cr_vjets_${channel}_e \
--regions cr_top_${channel}_m \
--regions cr_top_${channel}_e \
--output ${output} \
--threads ${threads}

if [[ ${1} == "condor" ]]; then
    ls -al
    xrdcp -rf ${output} root://cmseos.fnal.gov//store/user/rsingh/
    rm -rvf ${output}
    cd ../../
    ls -al
    rm -vf *docker*
fi

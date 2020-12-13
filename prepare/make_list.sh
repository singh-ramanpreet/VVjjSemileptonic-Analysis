#!/bin/bash

eos_in=${1}
year=${2}

list=$(eos root://cmseos.fnal.gov find --xurl -name "*.root" ${eos_in}/${year} | grep -Ev "Run${year}[A-Z]" > sample_list/${year}.txt)

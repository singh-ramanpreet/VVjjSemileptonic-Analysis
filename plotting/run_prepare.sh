#!/bin/bash

python3 -u prepare_dataset.py \
--datasets ../datasets_${1}.json \
--year ${1} \
--output ${1} \
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
--mva-var-list wjj_BDTG6/variable_list.txt \
&> ${1}_prepare.log &

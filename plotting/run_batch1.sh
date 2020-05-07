#!/bin/bash
export PYTHONUNBUFFERED=true

#mva_folder="wv_BDTG6"
#mva_tag="wv_BDTG6"

mva_folder="zjj_BDTG1"
mva_tag="zjj_BDTG1"

for i in "central" "jesUp" "jesDown"; do
    ./prepare_dataset.py \
    --datasets ../datasets_${1}.json \
    --year ${1} \
    --systematic ${i} \
    --mva ${mva_folder}/weights/VBS_BDT.weights.xml \
    --mva-var-list ${mva_folder}/variable_list.txt \
    --suffix-out ${mva_tag}
done

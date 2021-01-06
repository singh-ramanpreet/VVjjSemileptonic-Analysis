#!/bin/bash

export PYTHONUNBUFFERED=true

gridSearch=0
version_out="zjj_BDTG11"
mkdir -p ${version_out}
./train_BDTG.py \
  --in-files "root://cmseos.fnal.gov//eos/uscms/store/user/rsingh/wv_vbs_ntuples/training_input/2020_Dec_12/*.root" \
  --cut "lep2_pt > 20 && isAntiIso == 0 && lep1_q * lep2_q < 0 && dilep_m > 75 && dilep_m < 105 && \
         vbf_m > 500 && vbf1_AK4_pt > 50 && vbf2_AK4_pt > 50 && vbf_deta > 2.5 && \
         bos_AK4AK4_pt > 0 && bos_j2_AK4_pt > 30 && bos_j1_AK4_pt > 30 && \
         bos_AK4AK4_m > 65 && bos_AK4AK4_m < 105 && \
         ((lep_channel == 1 && \
             fabs(lep1_eta) < 2.5 && !(fabs(lep1_eta) > 1.4442 && fabs(lep1_eta) < 1.566) && \
             fabs(lep2_eta) < 2.5 && !(fabs(lep2_eta) > 1.4442 && fabs(lep2_eta) < 1.566) && lep1_pt > 25) \
             || (lep_channel == 0 && fabs(lep1_eta) < 2.4 && fabs(lep2_eta) < 2.4 && lep1_pt > 25))" \
  --boson Z \
  --ttree "Events" \
  --vars "lep2_eta,vbf_m,dibos_m,zeppLep_deta,ht_resolved" \
  --weights "xs_weight * genWeight" \
  --out-dir ${version_out} \
  --grid-search ${gridSearch} \
  --grid-search-nTrees 800 \
  --grid-search-minNode 3 \
  --grid-search-shrinkage 0.025 --grid-search-shrinkage 0.05 \
  --grid-search-baggFrac 0.6 \
  --BDT-NTrees 800 \
  --BDT-MinNodeSize 3 \
  --BDT-MaxDepth 3 \
  --BDT-nCuts 100 \
  --BDT-Shrinkage 0.025 \
  --BDT-BaggedFrac 0.6 2>&1 | tee ${version_out}/training.log

# remove ANSI color sequence
sed 's/\x1b\[[0-9;]*m//g' -i ${version_out}/training.log

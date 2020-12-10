#!/bin/bash

export PYTHONUNBUFFERED=true

version_out="zjj_BDTGXX"
mkdir -p ${version_out}
./train_BDTG.py \
  --in-files "root://cmseos.fnal.gov//store/user/singhr/test_prepare/2018/*.root" \
  --cut "lep2_pt > 20 && isAntiIso == 0 && lep1_q * lep2_q < 0 && dilep_m > 75 && dilep_m < 105 && \
         vbf_m > 500 && vbf1_AK4_pt > 50 && vbf2_AK4_pt > 50 && vbf_deta > 2.5 && \
         bos_AK4AK4_pt > 0 && bos_j2_AK4_pt > 30 && bos_j1_AK4_pt > 30 && \
         bos_AK4AK4_m > 65 && bos_AK4AK4_m < 105 && \
         ((lep_channel == 1 && \
             fabs(lep1_eta) < 2.5 && !(fabs(lep1_eta) > 1.4442 && fabs(lep1_eta) < 1.566) && \
             fabs(lep2_eta) < 2.5 && !(fabs(lep2_eta) > 1.4442 && fabs(lep2_eta) < 1.566) && lep1_pt > 40) \
             || (lep_channel == 0 && fabs(lep1_eta) < 2.4 && fabs(lep2_eta) < 2.4 && lep1_pt > 35))" \
  --boson Z \
  --ttree "Events" \
  --vars "lep2_eta,vbf_m,dibos_m,zeppLep_deta,ht_resolved" \
  --weights "xs_weight * genWeight" \
  --out-dir ${version_out} \
  --BDT-NTrees 400 \
  --BDT-MinNodeSize 6% \
  --BDT-MaxDepth 3 \
  --BDT-nCuts 100 \
  --BDT-Shrinkage 0.1 \
  --BDT-BaggedFrac 0.6 2>&1 | tee ${version_out}/training.log

# remove ANSI color sequence
sed 's/\x1b\[[0-9;]*m//g' -i ${version_out}/training.log

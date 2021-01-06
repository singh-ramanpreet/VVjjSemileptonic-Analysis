#!/bin/bash

export PYTHONUNBUFFERED=true

version_out="wjj_BDTGXX"
mkdir -p ${version_out}
./train_BDTG.py \
  --in-files "root://cmseos.fnal.gov//store/user/singhr/test_prepare/2018/*.root" \
  --cut "lep2_pt < 0 && isAntiIso == 0 && vbf_m > 500 && vbf1_AK4_pt > 50 && vbf2_AK4_pt > 50 && \
         vbf_deta > 2.5 && bosCent > 0.0 && fabs(zeppHad_deta) < 1.0 && fabs(zeppLep_deta) < 1.0 && \
         bos_AK4AK4_pt > 0 && bos_j2_AK4_pt > 30 && bos_j1_AK4_pt > 30 && \
         bos_AK4AK4_m > 65 && bos_AK4AK4_m < 105 && \
         ((lep_channel == 1 && fabs(lep1_eta) < 2.5 && !(fabs(lep1_eta) > 1.4442 && fabs(lep1_eta) < 1.566) && \
             lep1_pt > 35 && MET > 30) \
             || (lep_channel == 0 && fabs(lep1_eta) < 2.4 && \
             lep1_pt > 35 && MET > 30))" \
  --boson W \
  --ttree "Events" \
  --vars "lep1_pt,lep1_eta,MET,vbf_m,vbf1_AK4_pt,vbf1_AK4_eta,vbf2_AK4_pt,vbf2_AK4_eta,\
          bos_j1_AK4_pt,bos_j1_AK4_eta,bos_j2_AK4_pt,bos_j2_AK4_eta,bos_AK4AK4_m" \
  --weights "xs_weight * genWeight" \
  --out-dir ${version_out} \
  --BDT-NTrees 800 \
  --BDT-MinNodeSize 2.5% \
  --BDT-MaxDepth 3 \
  --BDT-nCuts 100 \
  --BDT-Shrinkage 0.005 \
  --BDT-BaggedFrac 0.6 2>&1 | tee ${version_out}/training.log

# remove ANSI color sequence
sed 's/\x1b\[[0-9;]*m//g' -i ${version_out}/training.log

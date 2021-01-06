#!/bin/bash

export PYTHONUNBUFFERED=true

version_out="wv_BDTGXX"
mkdir -p ${version_out}
./train_BDTG.py \
  --in-files "root://cmseos.fnal.gov//store/user/singhr/test_prepare/2018/*.root" \
  --cut "lep2_pt < 0 && isAntiIso == 0 && vbf_m > 500 && vbf1_AK4_pt > 50 && vbf2_AK4_pt > 50 && \
         vbf_deta > 2.5 && bosCent > 0.0 && fabs(zeppHad_deta) < 1.0 && fabs(zeppLep_deta) < 1.0 && \
         bos_PuppiAK8_pt > 200 && fabs(bos_PuppiAK8_eta) < 2.4 && bos_PuppiAK8_tau2tau1 < 0.55 && \
         bos_PuppiAK8_m_sd0_corr > 65 && bos_PuppiAK8_m_sd0_corr < 105 && \
         ((lep_channel == 1 && fabs(lep1_eta) < 2.5 && !(fabs(lep1_eta) > 1.4442 && fabs(lep1_eta) < 1.566) &&\
             lep1_pt > 35 && MET > 30) || \
             (lep_channel == 0 && fabs(lep1_eta) < 2.4 && \
             lep1_pt > 35 && MET > 30))" \
  --boson W \
  --ttree "Events" \
  --vars "lep1_pt,lep1_eta,MET,vbf_m,vbf1_AK4_pt,vbf1_AK4_eta,vbf2_AK4_pt,vbf2_AK4_eta,bos_PuppiAK8_pt,bos_PuppiAK8_eta" \
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

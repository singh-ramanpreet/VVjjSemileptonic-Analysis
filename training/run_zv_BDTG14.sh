#!/bin/bash

export PYTHONUNBUFFERED=true

gridSearch=0
version_out="zv_BDTG14"
mkdir -p ${version_out}
./train_BDTG.py \
  --in-files "root://cmseos.fnal.gov//eos/uscms/store/user/rsingh/2022-05-11_vvjj_ntuples/training_input/*.root" \
  --cut "lep2_pt > 20 && isAntiIso == 0 && lep1_q * lep2_q < 0 && dilep_m > 76 && dilep_m < 106 && \
         vbf_deta > 2.5 && \
         bos_PuppiAK8_pt > 200 && fabs(bos_PuppiAK8_eta) < 2.4 && \
         bos_PuppiAK8_m_sd0_corr > 65 && bos_PuppiAK8_m_sd0_corr < 105 && \
         nBtag_loose == 0 &&\
         ((lep_channel == 1 && fabs(lep1_eta) < 2.5 && !(fabs(lep1_eta) > 1.4442 && fabs(lep1_eta) < 1.566) && \
           fabs(lep2_eta) < 2.5 && !(fabs(lep2_eta) > 1.4442 && fabs(lep2_eta) < 1.566) && lep1_pt > 25) \
           || (lep_channel == 0 && fabs(lep1_eta) < 2.4 && fabs(lep2_eta) < 2.4 && lep1_pt > 25)) \
         && vbf1_AK4_qgid >= 0.0 && vbf1_AK4_qgid <= 1.0 \
         && vbf2_AK4_qgid >= 0.0 && vbf2_AK4_qgid <= 1.0" \
  --boson Z \
  --ttree "Events" \
  --vars "vbf_m,dibos_m,zeppLep_deta,vbf1_AK4_qgid,vbf2_AK4_qgid" \
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
  --BDT-Shrinkage 0.010 \
  --BDT-BaggedFrac 0.6 2>&1 | tee ${version_out}/training.log

# remove ANSI color sequence
sed 's/\x1b\[[0-9;]*m//g' -i ${version_out}/training.log

#!/bin/bash

export PYTHONUNBUFFERED=true

version_out="zv_BDTGXX"
mkdir -p ${version_out}
./train_BDTG.py \
  --in-files "root://cmseos.fnal.gov//store/user/singhr/test_prepare/2018/*.root" \
  --cut "lep2_pt > 20 && isAntiIso == 0 && lep1_q * lep2_q < 0 && dilep_m > 75 && dilep_m < 105 && \
         vbf_m > 500 && vbf1_AK4_pt > 50 && vbf2_AK4_pt > 50 && vbf_deta > 2.5 && \
         bos_PuppiAK8_pt > 200 && fabs(bos_PuppiAK8_eta) < 2.4 && bos_PuppiAK8_tau2tau1 < 0.55 && \
         bos_PuppiAK8_m_sd0_corr > 65 && bos_PuppiAK8_m_sd0_corr < 105 && \
         ((lep_channel == 1 && fabs(lep1_eta) < 2.5 && !(fabs(lep1_eta) > 1.4442 && fabs(lep1_eta) < 1.566) && \
           fabs(lep2_eta) < 2.5 && !(fabs(lep2_eta) > 1.4442 && fabs(lep2_eta) < 1.566) && lep1_pt > 25) \
           || (lep_channel == 0 && fabs(lep1_eta) < 2.4 && fabs(lep2_eta) < 2.4 && lep1_pt > 25))" \
  --boson Z \
  --ttree "Events" \
  --vars "vbf_m,dibos_m,zeppHad_deta" \
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

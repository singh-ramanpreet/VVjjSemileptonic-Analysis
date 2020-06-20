#!/bin/bash
export PYTHONUNBUFFERED=true

channel="wjj"
in_dir="2018_May11"

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
--output hists_${channel}.root

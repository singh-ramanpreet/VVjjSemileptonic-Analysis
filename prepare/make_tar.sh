#!/bin/bash

rm -v setup.tar.gz

tar -zcf setup.tar.gz -C ../../ WVAnalysis/ \
    --exclude="setup.tar.gz" \
    --exclude="*.root" \
    --exclude="*.ipynb*" \
    --exclude="*.pdf" \
    --exclude="*.png" \
    --exclude="*.err" \
    --exclude="*.out" \
    --exclude="*.log" \
    --exclude-caches-all --exclude-vcs


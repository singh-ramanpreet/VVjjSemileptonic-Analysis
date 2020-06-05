#!/bin/bash

tar -zcf setup.tar.gz -C ../../ WVAnalysis/ \
    --exclude="setup.tar.gz" \
    --exclude="*.root" \
    --exclude="*.ipynb*" \
    --exclude-caches-all --exclude-vcs


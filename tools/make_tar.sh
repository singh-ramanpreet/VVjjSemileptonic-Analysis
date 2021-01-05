#!/bin/bash

sandboxName=${1:-setup.tar.gz}

[[ -f ${sandboxName} ]] && rm -v ${sandboxName}

tar -zcf ${sandboxName} -C $ANALYSIS_BASE/.. $(basename $ANALYSIS_BASE)/ \
    --exclude-vcs \
    --exclude="*.tar.gz" \
    --exclude="*.root" \
    --exclude="*.pdf" \
    --exclude="*.png" \
    --exclude="*.err" \
    --exclude="*.out" \
    --exclude="*.log" \
    --exclude-caches-all

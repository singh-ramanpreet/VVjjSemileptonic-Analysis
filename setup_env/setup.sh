#!/bin/bash

DIR=$( dirname "${BASH_SOURCE[0]}" )
cd $DIR
source /cvmfs/sft.cern.ch/lcg/views/LCG_96python3/x86_64-centos7-gcc8-opt/setup.sh

export PYTHONUSERBASE=`pwd`
PY_VER=`python -c "import sys; print('python{0}.{1}'.format(*sys.version_info))"`
export PYTHONPATH=$PYTHONUSERBASE/lib/$PY_VER/site-packages:$PYTHONPATH
PATH=$PYTHONUSERBASE/bin:$PATH

echo "now installing pip pkgs"

pip install --user pip==20.0.2
pip install --user uproot==3.11.3
pip install --user uproot_methods==0.7.3
pip install --user awkward==0.12.20
pip install --user git+git://github.com/singh-ramanpreet/pyroot_cms_scripts.git@0.3.1

cd -

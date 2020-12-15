#!/bin/sh

histfile=${1}
year=${2}
z_cat=${3}
dyopt=${4:-1}
postfit=${5:-false}
postfit_var=${6:-mva_score_${z_cat}_var1}

if ! $postfit
then
  ../plot_variables.py --sys "jesTotal" --sys "qcd" -f ${histfile} -y ${year} -s cr_vjets_e -m ${z_cat} -B Z --dyjet-opt ${dyopt}
  ../plot_variables.py --sys "jesTotal" --sys "qcd" -f ${histfile} -y ${year} -s cr_vjets_m -m ${z_cat} -B Z --dyjet-opt ${dyopt}
  ../plot_variables.py --sys "jesTotal" --sys "qcd" -f ${histfile} -y ${year} -s cr_vjets_l -m ${z_cat} -B Z --dyjet-opt ${dyopt}
  ../plot_variables.py --sys "jesTotal" --sys "qcd" -f ${histfile} -y ${year} -s sr1_e -b -m ${z_cat} -B Z --dyjet-opt ${dyopt}
  ../plot_variables.py --sys "jesTotal" --sys "qcd" -f ${histfile} -y ${year} -s sr1_m -b -m ${z_cat} -B Z --dyjet-opt ${dyopt}
  ../plot_variables.py --sys "jesTotal" --sys "qcd" -f ${histfile} -y ${year} -s sr1_l -b -m ${z_cat} -B Z --dyjet-opt ${dyopt}
  ../plot_variables.py --sys "jesTotal" --sys "qcd" -f ${histfile} -y ${year} -s sr2_e -b -m ${z_cat} -B Z --dyjet-opt ${dyopt}
  ../plot_variables.py --sys "jesTotal" --sys "qcd" -f ${histfile} -y ${year} -s sr2_m -b -m ${z_cat} -B Z --dyjet-opt ${dyopt}
  ../plot_variables.py --sys "jesTotal" --sys "qcd" -f ${histfile} -y ${year} -s sr2_l -b -m ${z_cat} -B Z --dyjet-opt ${dyopt}
  #../plot_variables.py --sys "jesTotal" --sys "qcd" -f ${histfile} -y ${year} -s sr_e -b -m ${z_cat} -B Z --dyjet-opt ${dyopt}
  #../plot_variables.py --sys "jesTotal" --sys "qcd" -f ${histfile} -y ${year} -s sr_m -b -m ${z_cat} -B Z --dyjet-opt ${dyopt}
  #../plot_variables.py --sys "jesTotal" --sys "qcd" -f ${histfile} -y ${year} -s sr_l -b -m ${z_cat} -B Z --dyjet-opt ${dyopt}
else
 ../plot_variables.py -f ${histfile} -y ${year} -s sr1_l_postfit -m ${z_cat} -B Z --dyjet-opt ${dyopt}
 ../plot_variables.py -f ${histfile} -y ${year} -s sr2_l_postfit -m ${z_cat} -B Z --dyjet-opt ${dyopt}
fi

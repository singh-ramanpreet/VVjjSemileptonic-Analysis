#!/bin/sh

histfile=${1}
year=${2}
z_cat=${3}
postfit=${4:-false}
postfit_var=${5:-mva_score_${z_cat}_var2}

if ! $postfit
then
  ../plot_variables_v2.py --sys "jesTotal" --sys "qcd" -f ${histfile} -y ${year} -s cr_vjets_e -m ${z_cat} -B Z
  ../plot_variables_v2.py --sys "jesTotal" --sys "qcd" -f ${histfile} -y ${year} -s cr_vjets_m -m ${z_cat} -B Z
  ../plot_variables_v2.py --sys "jesTotal" --sys "qcd" -f ${histfile} -y ${year} -s cr_vjets_l -m ${z_cat} -B Z
  ../plot_variables_v2.py --sys "jesTotal" --sys "qcd" -f ${histfile} -y ${year} -s sr_e -b -m ${z_cat} -B Z --var mva_score_${z_cat}_var1 --var mva_score_${z_cat}_var2 --var mva_score_${z_cat}_var3
  ../plot_variables_v2.py --sys "jesTotal" --sys "qcd" -f ${histfile} -y ${year} -s sr_m -b -m ${z_cat} -B Z --var mva_score_${z_cat}_var1 --var mva_score_${z_cat}_var2 --var mva_score_${z_cat}_var3
  ../plot_variables_v2.py --sys "jesTotal" --sys "qcd" -f ${histfile} -y ${year} -s sr_l -b -m ${z_cat} -B Z --var mva_score_${z_cat}_var1 --var mva_score_${z_cat}_var2 --var mva_score_${z_cat}_var3
else
  ./post_fit_hists.py --in-root ${histfile} --in-sub-dir sr_l --fit-root datacards/fitDiagnostics_${year}_${z_cat}.root --fit-sub-dir shapes_fit_s/sr --sub-dirname sr_l_postfit --var-name ${postfit_var}
 ../plot_variables_v2.py -f ${histfile/.root/.sr_l_postfit.root} -y ${year} -s sr_l_postfit -m ${z_cat} -B Z --var ${postfit_var}
 #../plot_variables_v2.py -f ${histfile} -y ${year} -s sr1_l_postfit -m ${z_cat} -B Z --dyjet-opt ${dyopt}
 #../plot_variables_v2.py -f ${histfile} -y ${year} -s sr2_l_postfit -m ${z_cat} -B Z --dyjet-opt ${dyopt}
fi

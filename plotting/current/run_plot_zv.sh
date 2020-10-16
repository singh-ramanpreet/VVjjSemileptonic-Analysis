#!/bin/sh

histfile=${1}
year=${2}
dyopt=${3:-1}

../plot_variables.py --sys "jes" --sys "qcd" -f ${histfile} -y ${year} -s cr_vjets_e -m zv -B Z --dyjet-opt ${dyopt}
../plot_variables.py --sys "jes" --sys "qcd" -f ${histfile} -y ${year} -s cr_vjets_m -m zv -B Z --dyjet-opt ${dyopt}
../plot_variables.py --sys "jes" --sys "qcd" -f ${histfile} -y ${year} -s cr_vjets_l -m zv -B Z --dyjet-opt ${dyopt}
../plot_variables.py --sys "jes" --sys "qcd" -f ${histfile} -y ${year} -s cr_top_e -m zv -B Z --dyjet-opt ${dyopt}
../plot_variables.py --sys "jes" --sys "qcd" -f ${histfile} -y ${year} -s cr_top_m -m zv -B Z --dyjet-opt ${dyopt}
../plot_variables.py --sys "jes" --sys "qcd" -f ${histfile} -y ${year} -s cr_top_l -m zv -B Z --dyjet-opt ${dyopt}
../plot_variables.py --sys "jes" --sys "qcd" -f ${histfile} -y ${year} -s sr_e -b -m zv -B Z --dyjet-opt ${dyopt}
../plot_variables.py --sys "jes" --sys "qcd" -f ${histfile} -y ${year} -s sr_m -b -m zv -B Z --dyjet-opt ${dyopt} 
../plot_variables.py --sys "jes" --sys "qcd" -f ${histfile} -y ${year} -s sr_l -b -m zv -B Z --dyjet-opt ${dyopt}

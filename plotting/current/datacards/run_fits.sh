#!/bin/sh

datacard=${1/.txt/}

text2workspace.py ${datacard}.txt
combine -M FitDiagnostics -t -1 --expectSignal=1 ${datacard}.root --saveShapes --saveWithUncertainties --saveNormalizations  --robustFit 1 --cminDefaultMinimizerStrategy 0 --cminDefaultMinimizerTolerance 0.01 --plots --rMin -1.0 --rMax 3.0

#python mlfitNormsToText.py --uncertainties fitDiagnostics.root

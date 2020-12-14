#!/bin/sh

datacard=${1/.txt/}

text2workspace.py ${datacard}.txt
combine -M FitDiagnostics -t -1 --expectSignal=1 ${datacard}.root --name _${datacard} --saveShapes --saveWithUncertainties --saveNormalizations  --robustFit 1 --cminDefaultMinimizerStrategy 0 --cminDefaultMinimizerTolerance 0.01 --rMin -5.0 --rMax 6.0

#python mlfitNormsToText.py --uncertainties fitDiagnostics.root

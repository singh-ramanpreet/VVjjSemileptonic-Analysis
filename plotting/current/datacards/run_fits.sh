#!/bin/sh

for i in "2016_zv" "2017_zv" "2018_zv" "2016_zjj" "2017_zjj" "2018_zjj"
do
  datacard=${i}
  text2workspace.py ${datacard}.txt
  combine -M FitDiagnostics -t -1 --expectSignal=1 ${datacard}.root --name _${datacard} --saveShapes --saveWithUncertainties --saveNormalizations  --robustFit 1 --cminDefaultMinimizerStrategy 0 --cminDefaultMinimizerTolerance 0.01 --rMax 4.0 --rMin -4.0
done

#python mlfitNormsToText.py --uncertainties fitDiagnostics.root

#!/bin/sh

#for i in "2018_wv" "2018_wjj" "2018_zv" "2018_zjj";
#for i in "2018_wv_splitted" "2018_wjj_splitted" "2018_wv" "2018_wjj";
#for i in "run2_z";
for i in "2016_zv" "2017_zv" "2018_zv" "2016_zjj" "2017_zjj" "2018_zjj";
do
    text2workspace.py ${i}.txt
    
    combineTool.py -M Impacts -d ${i}.root -m 200 --robustFit 1 --doInitialFit  --cminDefaultMinimizerStrategy 0 \
    --cminDefaultMinimizerTolerance 0.01 -t -1 --expectSignal=1 --rMax 4.0 --rMin -2.0 

    combineTool.py -M Impacts -d ${i}.root -m 200 --robustFit 1 --doFits  --cminDefaultMinimizerStrategy 0 \
    --cminDefaultMinimizerTolerance 0.01 -t -1 --expectSignal=1 --rMax 4.0 --rMin -2.0
    
    combineTool.py -M Impacts -d ${i}.root -m 200 -o impacts_datacard_${i}.json
    
    plotImpacts.py -i impacts_datacard_${i}.json -o impacts_datacard_${i};

done

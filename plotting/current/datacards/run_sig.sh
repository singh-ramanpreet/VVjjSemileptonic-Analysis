#!/bin/bash

for i in "2016_zv" "2017_zv" "2018_zv" "run2_zv" "2016_zjj" "2017_zjj" "2018_zjj" "run2_zjj" "run2_z"
do
  echo ${i} $(combine -M Significance -t -1 --expectSignal=1 ${i}.txt | grep Significance:)
done

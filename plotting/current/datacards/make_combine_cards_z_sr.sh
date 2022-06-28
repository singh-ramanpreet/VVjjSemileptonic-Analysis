#!/bin/bash

main_card_z_sr="2016_zjj_sr.txt"
main_card_z_crDY="2016_zjj_cr_vjets.txt"

main_card_z="2016_zjj.txt"
combineCards.py sr=${main_card_z_sr} crDY=${main_card_z_crDY} > ${main_card_z}

sed -e 's/zjj/zv/g' ${main_card_z} > 2016_zv.txt

sed -e 's/2016/2017/g' ${main_card_z} > 2017_zjj.txt

sed -e 's/2016/2017/g' -e 's/zjj/zv/g' ${main_card_z} > 2017_zv.txt

sed -e 's/2016/2018/g' -e 's/^\(L1PF.*\)/#\1/g' -e 's/^\(nuisance.*L1PF.*\)/#\1/g' ${main_card_z} > 2018_zjj.txt

sed -e 's/2016/2018/g' -e 's/^\(L1PF.*\)/#\1/g' -e 's/^\(nuisance.*L1PF.*\)/#\1/g' -e 's/zjj/zv/g' ${main_card_z} > 2018_zv.txt

combineCards.py 2016_zv.txt 2017_zv.txt 2018_zv.txt &> run2_zv.txt

combineCards.py 2016_zjj.txt 2017_zjj.txt 2018_zjj.txt &> run2_zjj.txt

combineCards.py run2_zv.txt run2_zjj.txt &> run2_z.txt

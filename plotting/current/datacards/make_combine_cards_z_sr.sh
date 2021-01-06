#!/bin/bash

main_card_z_sr="2016_zjj_sr.txt"

sed -e 's/zjj/zv/g' ${main_card_z_sr} > 2016_zv_sr.txt

sed -e 's/2016/2017/g' ${main_card_z_sr} > 2017_zjj_sr.txt

sed -e 's/2016/2017/g' -e 's/zjj/zv/g' ${main_card_z_sr} > 2017_zv_sr.txt

sed -e 's/2016/2018/g' -e 's/^\(L1PF.*\)/#\1/g' -e 's/^\(nuisance.*L1PF.*\)/#\1/g' ${main_card_z_sr} > 2018_zjj_sr.txt

sed -e 's/2016/2018/g' -e 's/^\(L1PF.*\)/#\1/g' -e 's/^\(nuisance.*L1PF.*\)/#\1/g' -e 's/zjj/zv/g' ${main_card_z_sr} > 2018_zv_sr.txt

combineCards.py 2016_zv_sr.txt > 2016_zv.txt

combineCards.py 2017_zv_sr.txt > 2017_zv.txt

combineCards.py 2018_zv_sr.txt > 2018_zv.txt

combineCards.py 2016_zjj_sr.txt > 2016_zjj.txt

combineCards.py 2017_zjj_sr.txt > 2017_zjj.txt

combineCards.py 2018_zjj_sr.txt > 2018_zjj.txt

combineCards.py 2016_zv.txt 2017_zv.txt 2018_zv.txt &> run2_zv.txt

combineCards.py 2016_zjj.txt 2017_zjj.txt 2018_zjj.txt &> run2_zjj.txt

combineCards.py run2_zv.txt run2_zjj.txt &> run2_z.txt

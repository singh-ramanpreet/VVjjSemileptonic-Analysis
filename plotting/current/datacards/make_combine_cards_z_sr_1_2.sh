#!/bin/bash

main_card_z_sr1="2016_zjj_sr1.txt"
main_card_z_sr2="2016_zjj_sr2.txt"


sed -e 's/zjj/zv/g' ${main_card_z_sr1} > 2016_zv_sr1.txt
sed -e 's/zjj/zv/g' ${main_card_z_sr2} > 2016_zv_sr2.txt

sed -e 's/2016/2017/g' ${main_card_z_sr1} > 2017_zjj_sr1.txt
sed -e 's/2016/2017/g' ${main_card_z_sr2} > 2017_zjj_sr2.txt

sed -e 's/2016/2017/g' -e 's/zjj/zv/g' ${main_card_z_sr1} > 2017_zv_sr1.txt
sed -e 's/2016/2017/g' -e 's/zjj/zv/g' ${main_card_z_sr2} > 2017_zv_sr2.txt

sed -e 's/2016/2018/g' -e 's/^\(L1PF.*\)/#\1/g' -e 's/^\(nuisance.*L1PF.*\)/#\1/g' ${main_card_z_sr1} > 2018_zjj_sr1.txt
sed -e 's/2016/2018/g' -e 's/^\(L1PF.*\)/#\1/g' -e 's/^\(nuisance.*L1PF.*\)/#\1/g' ${main_card_z_sr2} > 2018_zjj_sr2.txt

sed -e 's/2016/2018/g' -e 's/^\(L1PF.*\)/#\1/g' -e 's/^\(nuisance.*L1PF.*\)/#\1/g' -e 's/zjj/zv/g' ${main_card_z_sr1} > 2018_zv_sr1.txt
sed -e 's/2016/2018/g' -e 's/^\(L1PF.*\)/#\1/g' -e 's/^\(nuisance.*L1PF.*\)/#\1/g' -e 's/zjj/zv/g' ${main_card_z_sr2} > 2018_zv_sr2.txt

combineCards.py 2016_zv_sr1.txt 2016_zv_sr2.txt > 2016_zv.txt

combineCards.py 2017_zv_sr1.txt 2017_zv_sr2.txt > 2017_zv.txt

combineCards.py 2018_zv_sr1.txt 2018_zv_sr2.txt > 2018_zv.txt

combineCards.py 2016_zjj_sr1.txt 2016_zjj_sr2.txt > 2016_zjj.txt

combineCards.py 2017_zjj_sr1.txt 2017_zjj_sr2.txt > 2017_zjj.txt

combineCards.py 2018_zjj_sr1.txt 2018_zjj_sr2.txt > 2018_zjj.txt

combineCards.py 2016_zv.txt 2017_zv.txt 2018_zv.txt &> run2_zv.txt

combineCards.py 2016_zjj.txt 2017_zjj.txt 2018_zjj.txt &> run2_zjj.txt

combineCards.py run2_zv.txt run2_zjj.txt &> run2_z.txt

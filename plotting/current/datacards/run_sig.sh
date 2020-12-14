#!/bin/bash

#combine -M Significance 2018_wv.txt -t -1 --expectSignal=1 | grep Significance:
#combine -M Significance 2018_wv_splitted.txt -t -1 --expectSignal=1 | grep Significance:
#combine -M Significance 2018_wjj.txt -t -1 --expectSignal=1 | grep Significance:
#combine -M Significance 2018_wjj_splitted.txt -t -1 --expectSignal=1 | grep Significance:
#combine -M Significance 2018_zv.txt -t -1 --expectSignal=1 | grep Significance:
#combine -M Significance 2018_zjj.txt -t -1 --expectSignal=1 | grep Significance:

combine -M Significance 2016_zv.txt -t -1 --expectSignal=1 | grep Significance:
combine -M Significance 2016_zjj.txt -t -1 --expectSignal=1 | grep Significance:

combine -M Significance 2017_zv.txt -t -1 --expectSignal=1 | grep Significance:
combine -M Significance 2017_zjj.txt -t -1 --expectSignal=1 | grep Significance:

combine -M Significance 2018_zv.txt -t -1 --expectSignal=1 | grep Significance:
combine -M Significance 2018_zjj.txt -t -1 --expectSignal=1 | grep Significance:

combine -M Significance run2_zv.txt -t -1 --expectSignal=1 | grep Significance:
combine -M Significance run2_zjj.txt -t -1 --expectSignal=1 | grep Significance:

combine -M Significance run2_z.txt -t -1 --expectSignal=1 | grep Significance:

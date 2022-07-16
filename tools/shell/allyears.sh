#!/bin/bash

STARTYEAR=1951
ENDYEAR=2021

for i in {1951..2021}
#for i in {1..3}
do
    python3 ./mcc_schedule.py -s $i -e $i -v > /Users/chris/sandbox/allyears/$i.txt
done

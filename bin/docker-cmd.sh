#!/bin/sh

# set elasticsearch mappings
mapping.sh
# create metar dir
mkdir /metar
# go to the metar dir
cd /metar
# get the first set
lftp -c mirror http://tgftp.nws.noaa.gov/data/observations/metar/cycles
# add station information
wget http://tgftp.nws.noaa.gov/data/nsd_cccc.txt
# do all the data
for x  in `ls *.TXT`; do echo $x ; cat $x | grep -E "^[A-Z]{4} " | sort -u | metar2elastic.py ; done
# set old_cycle
cp -r cycles old_cycles
#keep looping for ever
while [ 1 ]; do
   # mirror all metar data from noaa
   lftp -c mirror http://tgftp.nws.noaa.gov/data/observations/metar/cycles
   # post the diff in elasticsearch
   diff cycles/ old_cycles/ | grep -E "^\+[A-Z]{4}" | cut -d "+" -f 2 | sort -u | metar2elastic.py
   # remove old data
   rm -rf old_cycles
   # copy current to old data
   cp -r cycles old_cycles
   # wait 5 minutes
   sleep 300
done

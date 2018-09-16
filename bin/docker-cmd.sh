#!/bin/sh

echo "$(date) Starting METAR Weather"
# set elasticsearch mappings
mapping.sh
# go to the metar dir
cd /metar

# add station information
#wget -O - https://www.aviationweather.gov/docs/metar/stations.txt > stations.txt

#keep looping for ever
while [ 1 ]; do
  echo $(date)" Fetching new data"
  # get the first set
  lftp -c mirror http://tgftp.nws.noaa.gov/data/observations/metar/cycles
  # do all the data
  echo $(date)" Processing new data"
  for x  in `ls cycles/*.TXT`; do echo -n $(date)" "$x" " ; cat $x | grep -E "^[A-Z]{4} " | sort -u | metar2elastic.py ; done
  # remove cycles
  echo $(date)" Removing new data"
  # rm -rf cycles
  # wait
  echo $(date)" Sleeping 120 seconds"
  sleep 120
done

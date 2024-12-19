#!/bin/sh

echo "$(date) Starting METAR Weather"
# set elasticsearch mappings
/venv/bin/mapping.sh
# go to the metar dir
cd /metar

#keep looping for ever
while [ 1 ]; do
  echo $(date)" Fetching new data"
  # get the first set
  lftp -c mirror https://tgftp.nws.noaa.gov/data/observations/metar/cycles/
  # do all the data
  echo $(date)" Processing new data"
  for x  in `ls cycles/*.TXT`; do echo -n $(date)" "$x" " ; cat $x | grep -E "^[A-Z]{4} " | sort -u | /venv/bin/metar2elastic.py ; done
  echo $(date)" Sleeping 120 seconds"
  sleep 120
done

#!/usr/bin/python
import sys
import jsonpickle
import re
import os
from metar import Metar
from elasticsearch import Elasticsearch

if os.environ['ES_URL']:
    esurl="http://" + os.environ['ES_URL']
else:
    esurl="http://elastic:changeme@elasticsearch"

es = Elasticsearch([esurl], maxsize=5)

class MetarObj(object):

    def __init__(self):
        self.child = None

class position(object):
  """A class representing a location on the earth's surface."""

  def __init__( self, latitude=None, longitude=None ):
    self.latitude = latitude
    self.longitude = longitude

  def __str__(self):
    return self.string()

class station:
  """An object representing a weather station."""

  def __init__( self, id, city=None, state=None, country=None, latitude=None, longitude=None):
    self.id = id
    self.city = city
    self.state = state
    self.country = country
    self.position = position(latitude,longitude)
    if self.state:
      self.name = "%s, %s" % (self.city, self.state)
    else:
      self.name = self.city

def dms2dd(degrees, minutes, direction):
    dd = float(degrees) + float(minutes)/60
    if direction == 'S' or direction == 'W':
        dd *= -1
    return dd

def parse_dms(value):
    parts = re.split('(\d+|[A-Z])',value)
    value = dms2dd(parts[1], parts[3], parts[5])
    return (value)

#intialize station information
station_file_name = "/metar/nsd_cccc.txt"

stations = {}

fh = open(station_file_name,'r')
for line in fh:
  f = line.strip().split(";")
  stations[f[0]] = station(f[0],f[3],f[4],f[5],f[7],f[8])
fh.close()

#set counters
counter=0
missed=0
skipped=0
# read data from stdin
for line in sys.stdin:
    # remove enters
    line = line.strip()
    # create metar object
    metar = MetarObj()

    if len(line) and line[0] == line[0].upper():
      try:
        # decode the line
        obs = Metar.Metar(line)
        # Fill the metar object the individual data
        # The 'station_id' attribute is a string.
        if obs.station_id:
          metar.station_id=obs.station_id
          # set extra information about the station
          try:
            if stations[obs.station_id]:
              metar.position = str(parse_dms(stations[obs.station_id].position.latitude)) + "," + str(parse_dms(stations[obs.station_id].position.longitude))
              metar.country= stations[obs.station_id].country
              metar.city= stations[obs.station_id].city
          except:
              metar.country='unknown'
        # the report type
        if obs.type:
          metar.report_type=obs.report_type()

        # The 'time' attribute is a datetime object
        if obs.time:
          metar.time = obs.time.isoformat()

        # The 'temp' and 'dewpt' attributes are temperature objects
        if obs.temp:
          metar.temp = obs.temp.value("C")

        if obs.dewpt:
          metar.dewpt = obs.dewpt.value("C")

        # The wind() method returns a string describing wind observations
        # which may include speed, direction, variability and gusts.
        if obs.wind_dir:
             metar.wind_dir = obs.wind_dir.value()

        if obs.wind_speed:
          metar.wind_speed = obs.wind_speed.value("KMH")
          metar.wind = obs.wind("KMH")

        # The peak_wind() method returns a string describing the peak wind
        # speed and direction.
        if obs.wind_dir_peak:
          metar.wind_dir_peak = obs.wind_dir_peak.value()

        if obs.wind_speed_peak:
          metar.wind_speed_peak = obs.wind_speed_peak.value("KMH")
          metar.wind_speed_peak  = obs.peak_wind("KMH")

        # The visibility() method summarizes the visibility observation.
        if obs.vis:
          metar.visibility = obs.vis.value("m")

        # The runway_visual_range() method summarizes the runway visibility
        # observations.
        if obs.runway:
          metar.runway_visual_range = obs.runway_visual_range("m")

        # The 'press' attribute is a pressure object.
        if obs.press:
          metar.pressure = obs.press.value("hPa")

        # The 'precip_1hr' attribute is a precipitation object.
        if obs.precip_1hr:
          metar.precipitation = obs.precip_1hr.value("")

        # The present_weather() method summarizes the weather description (rain, etc.)
        try:
          weather = obs.present_weather()
          metar.weather=weather
        except:
          noweather=''

        # The sky_conditions() method summarizes the cloud-cover observations.
        try:
          sky = obs.sky_conditions()
          metar.sky=sky
        except:
          nosky=''

        # The remarks() method describes the remark groups that were parsed, but
        # are not available directly as Metar attributes.  The precipitation,
        # min/max temperature and peak wind remarks, for instance, are stored as
        # attributes and won't be listed here.
        if obs._remarks:
          metar.remarks = obs.remarks("")


        # set metar record
        record = jsonpickle.encode(metar,unpicklable=False)

        if obs.time:
          #timed index name
          myindex = "weather-" + obs.time.strftime("%Y%m%d%H")

          # build a search query to check if its there
          query = '{"query": { "bool": { "must": [{ "match": { "station_id": "' + metar.station_id + '"}},{ "match": { "time": "' + metar.time + '" }}]}}}'
          # check if the data is allready there
          try:
            res = es.search(index=myindex, doc_type='metar', body=query)
            if res['hits']['total'] == 0:
              # post the data to es
              res = es.index(index=myindex, doc_type='metar', body=record)
              counter += 1
            else:
              skipped += 1
          except:
            # posting, first record in index
            res = es.index(index=myindex, doc_type='metar', body=record)
            counter += 1
      except Metar.ParserError as exc:
        # store execptions for further investigation
        if exc:
          missed += 1
print ("%s records added, %s records where duplicates, %s records had errors") % (counter,skipped,missed)

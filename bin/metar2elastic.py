#!/usr/bin/python3
import sys
import jsonpickle
import os
import re
from metar import Metar
from elasticsearch import Elasticsearch

# connect to es
if os.environ['ES_URL']:
    esurl="http://" + os.environ['ES_URL']
else:
    esurl="http://elasticsearch:9200"

es = Elasticsearch([esurl], maxsize=5)

myindex = "metar"

class MetarObj(object):

  def __init__(self):
    self.station_id = None

class position(object):
  """A class representing a location on the earth's surface."""

  def __init__( self, latitude=None, longitude=None ):
    self.latitude = latitude
    self.longitude = longitude

  def __str__(self):
    return self.string()

class station:

  """An object representing a weather station.
!   CD = 2 letter state (province) abbreviation
!   STATION = 16 character station long name
!   ICAO = 4-character international id
!   IATA = 3-character (FAA) id
!   SYNOP = 5-digit international synoptic number
!   LAT = Latitude (degrees minutes)
!   LON = Longitude (degree minutes)
!   ELEV = Station elevation (meters)
!   M = METAR reporting station.   Also Z=obsolete? site
!   N = NEXRAD (WSR-88D) Radar site
!   V = Aviation-specific flag (V=AIRMET/SIGMET end point, A=ARTCC T=TAF U=T+V)
!   U = Upper air (rawinsonde=X) or Wind Profiler (W) site
!   A = Auto (A=ASOS, W=AWOS, M=Meso, H=Human, G=Augmented) (H/G not yet impl.)
!   C = Office type F=WFO/R=RFC/C=NCEP Center
!   Digit that follows is a priority for plotting (0=highest)
!   Country code (2-char) is last column
"""



  def __init__( self, id, state=None, station=None, iata=None, synop=None, lat=None, lon=None, elev=None, m=None, n=None, v=None, u=None, a=None, c=None, prio=None, country=None):

    self.id = id
    self.state = state
    self.station = station
    self.iata = iata
    self.synop = synop
    self.lat = self.parse_dms(lat)
    self.lon = self.parse_dms(lon)
    self.elev = elev
    if m != "":
      self.m = m
    if n != "":
      self.n = n
    if v != "":
      self.v = v
    if u != "":
      self.u = u
    if a != "":
      self.a = a
    if c != "":
      self.c = c
    self.prio = prio
    self.country = country


  def dms2dd(self, degrees, minutes, direction):
    dd = float(degrees) + float(minutes) / 60
    if direction == 'S' or direction == 'W':
        dd *= -1
    return dd


  def parse_dms(self, value):
    parts = re.split('(\d+|[A-Z])', value)
    value = self.dms2dd(parts[1], parts[3], parts[5])
    return value

#intialize station information
station_file_name = "/stations.txt"

stations = {}

fh = open(station_file_name,'r')

"""
ALASKA             19-SEP-14
CD  STATION         ICAO  IATA  SYNOP   LAT     LONG   ELEV   M  N  V  U  A  C
AK ADAK NAS         PADK  ADK   70454  51 53N  176 39W    4   X     T          7 US

"""
missed=0
for line in fh:
  line.strip()
  try:
    stations[line[20:24]] = station(line[20:24], line[0:2],line[3:19],line[26:29],line[32:37],line[39:45],line[47:54],line[56:59],line[62].strip(),line[65].strip(),line[68].strip(),line[71].strip(),line[74].strip(),line[77].strip(),line[79].strip(),line[81:83])
  except:
    missed += 1

fh.close()


#set counters
counter=0
missed=0
skipped=0
noinfo=0
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

        try:
            if stations[obs.station_id]:
                try:
                  metar.location = str(stations[obs.station_id].lat) + "," + str(stations[obs.station_id].lon)
                except:
                    noinfo += 1
                try:
                  metar.country = stations[obs.station_id].country
                except:
                    noinfo += 1
                try:
                  metar.station = stations[obs.station_id].station
                except:
                    noinfo += 1
                try:
                  metar.elev = int(stations[obs.station_id].elev)
                except:
                    noinfo += 1
                try:
                  metar.prio = int(stations[obs.station_id].prio)
                except:
                    noinfo += 1
        except:
          noinfo += 1

        # the report type
        if obs.report_type and obs.report_type() != "":
          metar.report_type=obs.report_type()

        # The 'time' attribute is a datetime object
        if obs.time:
          metar.time = obs.time.isoformat()

        # The 'temp' and 'dewpt' attributes are temperature objects
        if obs.temp:
          # temerature sanity check
          if obs.temp.value("C") > -70 and obs.temp.value("C") < 70:
            metar.temp = obs.temp.value("C")

        if obs.dewpt:
          # dewpoint sanity check
          if obs.dewpt.value("C") > 0 and obs.dewpt.value("C") < 40:
            metar.dewpt = obs.dewpt.value("C")

        # The wind() method returns a string describing wind observations
        # which may include speed, direction, variability and gusts.
        if obs.wind_dir:
          if obs.wind_dir.value() >= 0 and obs.wind_dir.value() < 360:
             metar.wind_dir = obs.wind_dir.value()

        if obs.wind_speed:
          if obs.wind_speed.value("KMH") >= 0 and obs.wind_speed.value("KMH") < 410:
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
        if obs.vis and obs.vis.value("m") != "":
          metar.visibility = obs.vis.value("m")

        # The runway_visual_range() method summarizes the runway visibility
        # observations.
        if obs.runway and obs.runway_visual_range("m") != "":
          metar.runway_visual_range = obs.runway_visual_range("m")

        # The 'press' attribute is a pressure object.
        if obs.press:
          if obs.press.value("hPa") > 860 and obs.press.value("hPa") < 1090:
            metar.pressure = obs.press.value("hPa")

        # The 'precip_1hr' attribute is a precipitation object.
        if obs.precip_1hr and obs.precip_1hr.value != 0:
          metar.precipitation = obs.precip_1hr.value("")

        # The present_weather() method summarizes the weather description (rain, etc.)
        try:
          if obs.present_weather() and obs.present_weather() != "":
            metar.weather=obs.present_weather()
        except:
          noweather=''

        # The sky_conditions() method summarizes the cloud-cover observations.
        try:
          if obs.sky_conditions() and obs.sky_conditions() != "":
            metar.sky=obs.sky_conditions()
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
          # build a search query to check if its there
          query = '{"query": {"bool": {"minimum_should_match": 4,"should": [{ "match": { "station_id.keyword": "' + metar.station_id + '"}},{ "match_phrase": { "time": "' + metar.time + '" }}]}}}'
          # check if the data is allready there
          #print (query)
          try:
            res = es.search(index=myindex, body=query)
            #print (res['hits']['total']['value'])
            if res['hits']['total']['value'] == 0:
              # post the data to es
              res = es.index(index=myindex, body=record)
              counter += 1
            else:
              skipped += 1
          except:
            # posting, first record in index
            res = es.index(index=myindex, body=record)
            counter += 1
      except Metar.ParserError as exc:
        # store execptions for further investigation
        if exc:
          missed += 1
print (("%s records added, %s records where duplicates, %s records had errors, %s missed info moments") % (counter,skipped,missed,noinfo))

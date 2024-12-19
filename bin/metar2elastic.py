#!/venv/bin/python3
import sys
import jsonpickle
import os
import re
import json
from metar import Metar
from elasticsearch import Elasticsearch

esurl = "http://elasticsearch:9200"

es = Elasticsearch([esurl], connections_per_node=5)

# remove static index
# myindex = "metar"


class MetarObj(object):

    def __init__(self):
        self.station_id = None


class position(object):
    """A class representing a location on the earth's surface."""

    def __init__(self, latitude=None, longitude=None):
        self.latitude = latitude
        self.longitude = longitude

    def __str__(self):
        return self.string()


class station:
    """An object representing a weather station."""
    def __init__(self, icaoId, state=None, site=None, iataId=None, wmoId=None, lat=None, lon=None, elev=None, m=None,
                 n=None, v=None, u=None, a=None, c=None, priority=None, country=None):
        self.id = icaoId
        self.state = state
        self.station = site
        self.iata = iataId
        self.synop = wmoId
        self.lat = lat
        self.lon = lon
        self.elev = elev
        self.m = m
        self.n = n
        self.v = v
        self.u = u
        self.a = a
        self.c = c
        self.prio = priority
        self.country = country


# intialize station information
station_file_name = "/stations.cache.json"

stations = {}

with open(station_file_name, 'r') as fh:
    data = json.load(fh)
    for entry in data:
        try:
            stations[entry['icaoId']] = station(
                entry['icaoId'],
                entry.get('state'),
                entry.get('site'),
                entry.get('iataId'),
                entry.get('wmoId'),
                entry.get('lat'),
                entry.get('lon'),
                entry.get('elev'),
                entry.get('m'),
                entry.get('n'),
                entry.get('v'),
                entry.get('u'),
                entry.get('a'),
                entry.get('c'),
                entry.get('priority'),
                entry.get('country')
            )
        except Exception as e:
            missed += 1

# set counters
counter = 0
missed = 0
skipped = 0
noinfo = 0
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
                metar.station_id = obs.station_id

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
                        metar.prio = int(stations[obs.station_id].priority)
                    except:
                        noinfo += 1
            except:
                noinfo += 1

            # the report type
            if obs.report_type and obs.report_type() != "":
                metar.report_type = obs.report_type()

            # The 'time' attribute is a datetime object
            if obs.time:
                metar.time = obs.time.isoformat()
                # create dynamic index name based on observation time
                myindex = f"metar-{obs.time.strftime('%Y-%m-%d')}"
                # create a unique _id using station_id and time
                doc_id = f"{metar.station_id}-{obs.time.strftime('%Y%m%d%H%M%S')}"

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
                metar.wind_speed_peak = obs.peak_wind("KMH")

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
                    metar.weather = obs.present_weather()
            except:
                noweather = ''

            # The sky_conditions() method summarizes the cloud-cover observations.
            try:
                if obs.sky_conditions() and obs.sky_conditions() != "":
                    metar.sky = obs.sky_conditions()
            except:
                nosky = ''

            # The remarks() method describes the remark groups that were parsed, but
            # are not available directly as Metar attributes.  The precipitation,
            # min/max temperature and peak wind remarks, for instance, are stored as
            # attributes and won't be listed here.
            if obs._remarks:
                metar.remarks = obs.remarks("")

            # set metar record
            record = jsonpickle.encode(metar, unpicklable=False)

            if obs.time:
                try:
                    # post the data to es with the unique _id
                    res = es.index(index=myindex, id=doc_id, body=record)
                    counter += 1
                except Exception as e:
                    # handle exception
                    missed += 1
        except Metar.ParserError as exc:
            missed += 1
print(f"{counter} records added, {skipped} records were duplicates, {missed} records had errors, {noinfo} missed info moments")


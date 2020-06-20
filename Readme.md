## MetarWeather

METAR reports are airport weather reports from all over the world.
This project mirrors NOAA METAR cycles and stores it in elasticsearch.

### Usage

After about 10 minutes(depending on internet speed etc.)
the data starts flowing into elasticsearch.

#### View your data in kibana with your browser

http://<docker-host>:5601


Kibana config (add index paterns)
Index name or pattern: metar
Time-field name: time

![Wind map example](https://github.com/danielguerra69/metar-weather/blob/master/images/wind.png)

![Temperature map example](https://github.com/danielguerra69/metar-weather/blob/master/images/temperature.png)

#### Automatic docker-compose method

Clone this repository

```bash
git clone https://github.com/danielguerra69/metar-weather.git
cd metar-weather
```

Build it, run it, check it, log it

```bash
docker-compose build
docker-compose up -d
docker-compose status
docker-compose logs -f
```

#### Manual docker method
First start elasticsearch
```bash
docker run --name es -d docker.elastic.co/elasticsearch/elasticsearch:6.4.0
```

Second start kibana
```bash
docker run -p 5601:5601 --link es:elasticsearch --name kb -d docker.elastic.co/kibana/kibana:6.4.0
```

Third start metar weather
```bash
docker run -d --name metar --link es:elasticsearch danielguerra/metar-weather
```

After about 10 minutes(depending on internet speed etc.)
the data starts flowing into elasticsearch. To be sure
check the logs for 00Z.TXT ...

```bash
docker logs metar
```


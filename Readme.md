## MetarWeather

This project mirrors NOAA metar cycles and stores it in elasticsearch.

### Usage

The project was created with elasticsearch xpack.

First start elasticsearch
```bash
docker run --name es-xpack -d danielguerra/elasticsearch-x-pack
```

Second start kibana
```bash
docker run -p 5601:5601 --link es-xpack:elasticsearch --name kb-xpack -d danielguerra/kibana-x-pack
```

Third start metar weather
```bash
docker run -d --name metar --link es-xpack:elasticsearch danielguerra/metar-weather
```

After about 10 minutes(depending on internet speed etc.)
the data starts flowing into elasticsearch. To be sure
check the logs for 00Z.TXT ...

```bash
docker logs metar
```

Finally check your data in kibana with your browser

http://<docker-host>:5601

Credentials
user: elastic
pass: changeme

Kibana config (index creation)
index: weather-*
date: time

#!/bin/sh
until curl -XGET elastic:changeme@elasticsearch:9200/; do
  >&2 echo "Elasticsearch is unavailable - sleeping"
  sleep 5
done

>&2 echo "Elasticsearch is up - executing command"
curl -XPUT elastic:changeme@elasticsearch:9200/_template/fixpos_weather -d '{
  "template": "weather-*",
    "index": {
      "number_of_shards": 3,
      "number_of_replicas": 1
    },
    "mappings" : {
      "metar" : {
          "properties" : {
            "position" : {
              "type" : "geo_point"
            }
          }
      }
    }
  }'

echo ""

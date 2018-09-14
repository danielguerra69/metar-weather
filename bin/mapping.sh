#!/bin/sh

if [ -z "$ES_URL" ]; then
  ES_URL="elastic:changeme@elasticsearch:9200"
fi

echo "$(date) Mapping Using ES_URL $ES_URL"

until curl -XGET $ES_URL -H 'Content-Type: application/json'; do
  >&2 echo "$(date) Elasticsearch is unavailable - sleeping"
  sleep 5
done

>&2 echo "$(date) Elasticsearch is up - executing command"
curl -XPUT $ES_URL/_template/fixpos_weather -H 'Content-Type: application/json' -d '{
  "template": "weather-*",
    "index": {
      "number_of_shards": 3,
      "number_of_replicas": 1
    },
    "mappings" : {
      "metar" : {
          "properties" : {
            "time" : {
                "type" : "date"
            },
            "position" : {
              "type" : "geo_point"
            }
          }
      }
    }
  }'
echo " "
echo "$(date) Mapping finished"

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
curl -XPUT $ES_URL/_template/metar_mapping -H 'Content-Type: application/json' -d '{
  "template": "metar-*",
    "index": {
      "number_of_shards": 3,
      "number_of_replicas": 1
    },
    "mappings" : {
      "metar" : {
        "properties" : {
          "country" : {
            "type" : "text",
            "fields" : {
              "keyword" : {
                "type" : "keyword",
                "ignore_above" : 2
              }
            }
          },
          "dewpt" : {
            "type" : "float"
          },
          "elev" : {
            "type" : "float"
          },
          "location" : {
            "type" : "geo_point"
          },
          "precipitation" : {
            "type" : "float"
          },
          "pressure" : {
            "type" : "float"
          },
          "prio" : {
            "type" : "float"
          },
          "remarks" : {
            "type" : "text",
            "fields" : {
              "keyword" : {
                "type" : "keyword",
                "ignore_above" : 256
              }
            }
          },
          "report_type" : {
            "type" : "text",
            "fields" : {
              "keyword" : {
                "type" : "keyword",
                "ignore_above" : 256
              }
            }
          },
          "runway_visual_range" : {
            "type" : "text",
            "fields" : {
              "keyword" : {
                "type" : "keyword",
                "ignore_above" : 256
              }
            }
          },
          "sky" : {
            "type" : "text",
            "fields" : {
              "keyword" : {
                "type" : "keyword",
                "ignore_above" : 256
              }
            }
          },
          "station" : {
            "type" : "text",
            "fields" : {
              "keyword" : {
                "type" : "keyword",
                "ignore_above" : 256
              }
            }
          },
          "station_id" : {
            "type" : "text",
            "fields" : {
              "keyword" : {
                "type" : "keyword",
                "ignore_above" : 256
              }
            }
          },
          "temp" : {
            "type" : "float"
          },
          "time" : {
            "type" : "date"
          },
          "visibility" : {
            "type" : "float"
          },
          "weather" : {
            "type" : "text",
            "fields" : {
              "keyword" : {
                "type" : "keyword",
                "ignore_above" : 256
              }
            }
          },
          "wind" : {
            "type" : "text",
            "fields" : {
              "keyword" : {
                "type" : "keyword",
                "ignore_above" : 256
              }
            }
          },
          "wind_dir" : {
            "type" : "float"
          },
          "wind_dir_peak" : {
            "type" : "float"
          },
          "wind_speed" : {
            "type" : "float"
          },
          "wind_speed_peak" : {
            "type" : "text",
            "fields" : {
              "keyword" : {
                "type" : "keyword",
                "ignore_above" : 256
              }
            }
          }
        }
      }
    }
  }'
echo " "
echo "$(date) Mapping finished"

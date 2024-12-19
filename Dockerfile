FROM alpine
LABEL maintainer="Daniel Guerra"

RUN apk add --update --no-cache py-pip lftp curl python3 py3-virtualenv gzip
RUN python3 -m venv /venv
RUN /venv/bin/pip install --no-cache-dir elasticsearch python-metar jsonpickle requests
RUN wget -O stations.cache.json.gz https://aviationweather.gov/data/cache/stations.cache.json.gz
RUN gzip -d stations.cache.json.gz
RUN rm -rf /root/.cache
COPY bin /venv/bin
VOLUME /metar
CMD ["/bin/sh", "-c", ". /venv/bin/activate && /venv/bin/docker-cmd.sh"]

FROM alpine
LABEL maintainer="Daniel Guerra"

RUN apk add --update --no-cache py-pip lftp curl python3 py3-virtualenv
RUN python3 -m venv /venv
RUN /venv/bin/pip install --no-cache-dir elasticsearch python-metar jsonpickle https://github.com/exTerEX/noaa/tarball/main
RUN wget http://www.moratech.com/aviation/metar-stations.txt
RUN rm -rf /root/.cache
COPY bin /bin
VOLUME /metar
CMD ["/bin/sh", "-c", ". /venv/bin/activate && /bin/docker-cmd.sh"]

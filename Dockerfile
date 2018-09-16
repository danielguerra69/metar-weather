FROM alpine
MAINTAINER Daniel Guerra

RUN apk add --update --no-cache py-pip lftp curl
RUN pip install --no-cache-dir --upgrade pip
RUN pip install --no-cache-dir elasticsearch python-metar jsonpickle
RUN wget https://www.aviationweather.gov/docs/metar/stations.txt
RUN rm -rf /root/.cache
COPY bin /bin
VOLUME /metar
CMD ["/bin/docker-cmd.sh"]

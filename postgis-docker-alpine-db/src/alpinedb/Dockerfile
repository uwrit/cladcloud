# Postgis
FROM postgis/postgis:16-3.4-alpine

# Configure utils
#RUN apt-get update \
#    && apt-get install -y wget unzip postgis \
#    && rm -rf /var/lib/apt/lists/*

## run apk instead on alpine to install key tools
RUN apk add wget unzip postgis libintl

# Make data dir
RUN mkdir -p /gisdata \
    && chmod 777 -R /gisdata

# Copy nation an state scripts
COPY ./load_data.sh /docker-entrypoint-initdb.d/

# Overwrite the default /postgis.sh file
COPY ./postgis.sh /docker-entrypoint-initdb.d/

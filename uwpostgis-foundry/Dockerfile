FROM postgis/postgis:16-3.5-alpine AS buildtime_init_builder

ARG POSTGRES_DB=geocoder      
ARG POSTGRES_USER=clad_svc     
ARG POSTGRES_PASSWORD=not_on_gitlab   
ARG GEOCODER_STATES=AK  
ARG GEOCODER_YEAR=2020

SHELL ["/bin/bash", "-c"]

RUN apk add wget unzip postgis libintl
# Make data dir
RUN mkdir -p /gisdata \
    && chmod 777 -R /gisdata

#download state data in separate layer
COPY ./src/alpinedb/state_download_layer.sh .
RUN ./state_download_layer.sh 

ENV PGDATA=/pgdata

# https://stackoverflow.com/questions/34751814/build-postgres-docker-container-with-initial-schema
# Initialize the database during the build
# PART 1
COPY ./src/alpinedb/1-load_data.sh /docker-entrypoint-initdb.d/
RUN echo "docker_temp_server_stop && exit 0" > /docker-entrypoint-initdb.d/900-exit_before_boot.sh
RUN docker-entrypoint.sh postgres


FROM postgis/postgis:16-3.5-alpine AS buildtime_init

SHELL ["/bin/bash", "-c"]

RUN adduser --uid 5001 --disabled-password user

## run apk instead on alpine to install key tools
RUN apk update
RUN apk add wget unzip postgis libintl python3 py3-pip python3-dev py3-psycopg vim 
    
ENV PGDATA=/pgdata


# Foundry customizations
RUN mkdir -p /opt/palantir/sidecars/shared-volumes/shared/
RUN chown 5001 /opt/palantir/sidecars/shared-volumes/shared/
ENV SHARED_DIR=/opt/palantir/sidecars/shared-volumes/shared

RUN python3 -m venv foundry_venv
COPY requirements.txt ./
RUN /foundry_venv/bin/pip install --no-cache-dir -r requirements.txt

ADD entrypoint.py /usr/bin/entrypoint
RUN chmod +x /usr/bin/entrypoint

COPY process_csv.py ./

WORKDIR /opt/palantir/sidecars/shared-volumes/shared/

RUN chown -R 5001:5001 /tmp /foundry_venv /var/run/postgresql

# https://stackoverflow.com/questions/34751814/build-postgres-docker-container-with-initial-schema
# Initialize the database during the build
# PART 2
## copy database from initialization layer
RUN mkdir -m 700 /pgdata 
RUN chown 5001:5001 /pgdata
COPY --chown=5001:5001 --chmod=700 --from=buildtime_init_builder /pgdata /pgdata


USER 5001

ENTRYPOINT entrypoint -c "/foundry_venv/bin/python3 /process_csv.py"


# https://stackoverflow.com/questions/34751814/build-postgres-docker-container-with-initial-schema
# Initialize the database during the build
# PART 1
FROM postgis/postgis:17-3.5-alpine AS db_creator

# copy statics
RUN mkdir -m 777 /gisdata
COPY ./src/alpinedb/download_national.sh .
COPY ./src/alpinedb/download_state.sh .
COPY ./src/alpinedb/1-load_data.sh /docker-entrypoint-initdb.d/

# national data first
# build vars
ARG TIGER_DOMAIN
ARG POSTGRES_DB=geocoder
ARG POSTGRES_USER=clad_svc
ARG POSTGRES_PASSWORD=not_on_gitlab
ARG GEOCODER_YEAR=2020

# runtime vars
ENV TIGER_DOMAIN=${TIGER_DOMAIN}
ENV PGDATA=/pgdata

SHELL ["/bin/bash", "-c"]
RUN apk add libintl postgis unzip wget
RUN echo "docker_temp_server_stop && exit 0" > /docker-entrypoint-initdb.d/900-exit_before_boot.sh
RUN ./download_national.sh

# state data second
# ARG forces build to not use cache from a previous state(s) build:
ARG state_var
ENV STATES=${state_var}
RUN ./download_state.sh

RUN bash -x docker-entrypoint.sh postgres


# PART 2
FROM postgis/postgis:17-3.5-alpine
# not used, old, and has CVEs
RUN rm -f /usr/local/bin/gosu

# copy statics
RUN mkdir -m 700 /pgdata
ENV PGDATA=/pgdata

RUN apk upgrade --no-cache
RUN apk add py3-pip
RUN python3 -m pip install --break-system-packages --no-cache-dir --upgrade pip
RUN python3 -m pip freeze | sed 's/==/>=/g' | xargs python3 -m pip install --break-system-packages --no-cache-dir --upgrade

SHELL ["/bin/bash", "-c"]

# Foundry customizations
RUN adduser --uid 5001 --disabled-password user
RUN mkdir -p /opt/palantir/sidecars/shared-volumes/shared/
RUN chown 5001 /opt/palantir/sidecars/shared-volumes/shared/
ENV SHARED_DIR=/opt/palantir/sidecars/shared-volumes/shared

COPY requirements.txt /
COPY --chmod=0755 process_csv.py /
COPY --chmod=0755 entrypoint.py /usr/bin/entrypoint
RUN pip install --break-system-packages --no-cache-dir -r /requirements.txt

# copy database from db_creator
COPY --chmod=700 --from=db_creator /pgdata /pgdata
RUN chown -R 5001:5001 /tmp /var/run/postgresql /pgdata
ARG state_var
RUN echo "$state_var" > /pgdata/states

WORKDIR /opt/palantir/sidecars/shared-volumes/shared/
USER 5001
ENTRYPOINT entrypoint -c "/process_csv.py"

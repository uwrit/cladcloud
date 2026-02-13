# https://stackoverflow.com/questions/34751814/build-postgres-docker-container-with-initial-schema
# Initialize the database during the build
# PART 1
FROM postgis/postgis:18-3.6-alpine AS db_creator
SHELL ["/bin/bash", "-c"]

# copy statics
COPY --chmod=0755 --chown=postgres:postgres load_data.sh /docker-entrypoint-initdb.d/11-load_data.sh

# build vars
ARG TIGER_DOMAIN
ARG YEAR=2024

# runtime vars
ENV DOMAIN=${TIGER_DOMAIN}
ENV YEAR=${YEAR}
ENV PGDATA=/pgdata
ENV POSTGRES_DB=geocoder
ENV POSTGRES_PASSWORD=not_on_gitlab
ENV POSTGRES_USER=postgres

RUN echo "docker_temp_server_stop && exit 0" > /docker-entrypoint-initdb.d/900-exit_before_boot.sh
RUN apk add libintl wget
RUN echo "check_certificate = off" >> /etc/wgetrc

# state data second
# ARG forces build to not use cache from a previous state(s) build:
ARG state_var
ENV STATES=${state_var}

# start postgres and load the data
RUN mkdir -m 777 /gisdata
RUN chown -R postgres:postgres /gisdata
RUN bash -x docker-entrypoint.sh postgres


# PART 2
FROM postgis/postgis:18-3.6-alpine
SHELL ["/bin/bash", "-c"]
# not used, old, and has CVEs
RUN rm -f /usr/local/bin/gosu

# copy statics
RUN mkdir -m 700 /pgdata
ENV PGDATA=/pgdata

RUN apk upgrade --no-cache
RUN apk add py3-pip
RUN python3 -m pip install --break-system-packages --no-cache-dir pandas psycopg tqdm
RUN python3 -m pip install --break-system-packages --no-cache-dir --upgrade pip
RUN python3 -m pip freeze | sed 's/==/>=/g' | xargs python3 -m pip install --break-system-packages --no-cache-dir --upgrade

# Foundry customizations
RUN adduser --uid 5001 --disabled-password user
RUN mkdir -p /opt/palantir/sidecars/shared-volumes/shared/
RUN chown 5001 /opt/palantir/sidecars/shared-volumes/shared/
ENV SHARED_DIR=/opt/palantir/sidecars/shared-volumes/shared

COPY --chmod=0755 process_csv.py /
COPY --chmod=0755 entrypoint.py /usr/bin/entrypoint

# copy database from db_creator
COPY --chmod=700 --from=db_creator /pgdata /pgdata
RUN chown -R 5001:5001 /tmp /var/run/postgresql /pgdata
ARG state_var
RUN echo "$state_var" > /pgdata/states

WORKDIR /opt/palantir/sidecars/shared-volumes/shared/
USER 5001
ENTRYPOINT ["entrypoint", "-c", "/process_csv.py"]

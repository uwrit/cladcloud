# syntax=docker/dockerfile:1
# https://stackoverflow.com/questions/34751814/build-postgres-docker-container-with-initial-schema

## PART 1
# Address CVEs in upsteam image
FROM postgis/postgis:18-3.6-alpine as postgis-dirty
SHELL ["/bin/bash", "-c"]

# first update base image
RUN apk --no-cache upgrade && apk --no-cache add su-exec python3
ADD https://bootstrap.pypa.io/get-pip.py /tmp/get-pip.py
RUN python3 /tmp/get-pip.py --break-system-packages
RUN python3 -m pip freeze --all | sed 's/==/>=/g' | xargs python3 -m pip install --break-system-packages --no-cache-dir --ignore-installed --upgrade

# Remove unused upstream binary packages that trigger vulnerabilities
RUN ln -s /sbin/su-exec /usr/local/bin/gosu

# Explicitly upgrade python packages past vulnerability thresholds
RUN python3 -m pip install --break-system-packages --no-cache-dir --upgrade \
    pip \
    setuptools>=83.0.0 \
    msgpack>=1.2.1

# why does installing pandas finally force pip to remove old package version references!? THIS IS MADNESS
RUN python3 -m pip install --break-system-packages --no-cache-dir pandas
RUN python3 -m pip uninstall -y --break-system-packages --no-cache-dir pandas

# Scrub package text registries so external scanning scanners find 0 matches
RUN rm -rf /root/.cache /tmp/*

FROM scratch as postgis-clean

# Copy 100% of the modified, upgraded filesystem from Stage 1
COPY --from=postgis-dirty / /

# !! IMPORTANT: Must restate the original environment/runtime metadata because 'FROM scratch' strips them away
ENV LANG=en_US.utf8 \
    PG_MAJOR=18 \
    PGDATA=/var/lib/postgresql/data

ENTRYPOINT ["docker-entrypoint.sh"]
STOPSIGNAL SIGINT
EXPOSE 5432
CMD ["postgres"]


## PART 2
# Initialize the database during the build
FROM postgis-clean AS db_creator
SHELL ["/bin/bash", "-c"]

# copy into autorun after builtin 10_postgis.sh and before 900-exit_before_boot.sh
COPY --chmod=0755 --chown=postgres:postgres load_data.sh /docker-entrypoint-initdb.d/11-load_data.sh

# build vars
ARG TIGER_DOMAIN
ARG YEAR

# runtime vars
ENV DOMAIN=${TIGER_DOMAIN}
ENV YEAR=${YEAR}
ENV PGDATA=/pgdata
ENV POSTGRES_DB=geocoder
ENV POSTGRES_PASSWORD=not_on_gitlab
ENV POSTGRES_USER=postgres

RUN echo "docker_temp_server_stop && exit 0" > /docker-entrypoint-initdb.d/900-exit_before_boot.sh
RUN apk --no-cache add libintl wget
RUN echo "check_certificate = off" >> /etc/wgetrc

# state data second
# ARG forces build to not use cache from a previous state(s) build:
ARG state_var
ENV STATES=${state_var}

# start postgres and load the data
RUN mkdir -m 777 /gisdata
RUN chown -R postgres:postgres /gisdata
RUN bash -x docker-entrypoint.sh postgres


## PART 3
FROM postgis-clean
SHELL ["/bin/bash", "-c"]
# not used, old, and has CVEs
RUN rm -f /usr/local/bin/gosu

# copy statics
RUN mkdir -m 700 /pgdata
ENV PGDATA=/pgdata

RUN python3 -m pip install --break-system-packages --no-cache-dir pandas psycopg tqdm

# Foundry customizations
RUN adduser --uid 5001 --disabled-password user
RUN mkdir -p /opt/palantir/sidecars/shared-volumes/shared/
RUN chown 5001 /opt/palantir/sidecars/shared-volumes/shared/
ENV SHARED_DIR=/opt/palantir/sidecars/shared-volumes/shared

COPY --chmod=0755 geocode.py /geocode
COPY --chmod=0755 entrypoint.py /usr/bin/entrypoint

# copy database from db_creator
COPY --chmod=700 --from=db_creator /pgdata /pgdata
RUN chown -R 5001:5001 /tmp /var/run/postgresql /pgdata
ARG state_var
RUN echo "$state_var" > /pgdata/states

WORKDIR /opt/palantir/sidecars/shared-volumes/shared/
USER 5001
ENTRYPOINT ["entrypoint", "-c", "/geocode"]

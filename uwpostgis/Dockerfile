## PART 1 - https://stackoverflow.com/questions/34751814/build-postgres-docker-container-with-initial-schema
# Initialize the database during the build
FROM postgis/postgis:18-3.6-alpine AS db_creator

# install load_data.sh (loader_generate_nation_script) dependencies
RUN apk --no-cache add libintl wget
RUN echo "docker_temp_server_stop && exit 0" > /docker-entrypoint-initdb.d/900-exit_before_boot.sh
RUN echo "check_certificate = off" >> /etc/wgetrc
RUN mkdir -m 777 /gisdata
RUN chown -R postgres:postgres /gisdata

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

# state data second
# ARG forces build to not use cache from a previous state(s) build:
ARG state_var
ENV STATES=${state_var}

# start postgres and load the data
RUN bash -x docker-entrypoint.sh postgres


## PART 2
# Address CVEs in upsteam image
FROM postgis/postgis:18-3.6-alpine as postgis-dirty

# first update base image
# RUN apk --no-cache del $(apk info | grep -E '^go(-|$)|golang')
# upgrade apk first
RUN apk --no-cache add --upgrade apk-tools
# then upgrade the system
RUN apk --no-cache upgrade
RUN apk --no-cache add py3-pip
# Create a permanent executable wrapper for pip
RUN echo -e '#!/bin/bash\nexec python3 -m pip install --break-system-packages --no-cache-dir --ignore-installed "$@"' > /usr/local/bin/pipi && \
    chmod +x /usr/local/bin/pipi
# update all python packages
RUN python3 -m pip freeze --all | sed 's/==/>=/g' | xargs pipi --upgrade

# install dependencies
RUN pipi pandas psycopg tqdm

# ADDRESS CVEs:
# not used, old, and has CVEs
RUN rm -f /usr/local/bin/gosu
# drop old tracking stubs that package managers refused to overwrite - eliminates all vulnerable paths caught in Trivy scans
RUN find /usr/lib/python* -type d \( \
    -name "*license*" -o \
    -name "msgpack-1.1.2*" -o \
    -name "pip-26.1.2*" -o \
    -name "setuptools-70.3.0*" -o \
    \) -exec rm -rf {} +
RUN rm -rf /usr/lib/python*/ensurepip \
    /usr/lib/python*/site-packages/msgpack*/_vendor \
    /usr/lib/python*/site-packages/pip*/_vendor/msgpack* \
    /usr/lib/python*/site-packages/pip*/_vendor/setuptools* \
    /usr/lib/python*/site-packages/pkg_resources*/_vendor \
    /usr/lib/python*/site-packages/setuptools*/_vendor
# remove all references to deleted python binaries
RUN find /usr/lib/python* \( \
    -iname "*.json" -o \
    -iname "*.txt" -o \
    -iname "*.whl" -o \
    \) -delete

# see if pip still runs?
RUN python3 -m pip freeze --all

# ─── THE ULTIMAL CRUFT STRIPPER (NON-FUNCTIONAL FILES) ───
# strip all language-specific test suites, examples, and non-functional docs
RUN find /usr/lib/python* -type d \( \
    -name "doc" -o \
    -name "docs" -o \
    -name "examples" -o \
    -name "idlelib" -o \
    -name "test" -o \
    -name "tests" -o \
    -name "turtledemo" -o \
    \) -exec rm -rf {} +

# strip broad system-level documentation, localized manual pages, and help guides
RUN rm -rf /usr/share/doc \
    /usr/share/gtk-doc \
    /usr/share/help/* \
    /usr/share/info \
    /usr/share/man

# strip C/C++ development header artifacts (.h files)
RUN find /usr/include /usr/lib/python* -name "*.h" -delete

# strip all python bytecode translation caches (__pycache__)
RUN find /usr/lib/python* -name "__pycache__" -type d -exec rm -rf {} +

# strip fallback package indexing database binaries left by apk and pip
RUN rm -rf /lib/apk/db/scripts.tar \
    /var/cache/apk/*


# PART 3 - The Ultimate Clean Runtime Stage
# --squash is deprecated, --output squash=true is broken, COPY --from=dirty / / copies all layer junk (deleted files) as well, tar export/import doubles output container size, so copy main folders individually from previous step to get JUST the files and NOTHING from the deleted layers
FROM scratch as postgis

COPY --from=postgis-dirty /bin /bin
COPY --from=postgis-dirty /etc /etc
COPY --from=postgis-dirty /lib /lib
COPY --from=postgis-dirty /sbin /sbin
COPY --from=postgis-dirty /usr /usr
RUN mkdir -m 777 /app
RUN mkdir -m 777 /tmp
RUN mkdir -m 777 -p /var/run/postgresql
ENV PGDATA=/pgdata
COPY --chmod=0755 geocode.py /app/geocode

# Foundry customizations
RUN adduser --uid 5001 --disabled-password user
RUN mkdir -p /opt/palantir/sidecars/shared-volumes/shared/
RUN chown 5001 /opt/palantir/sidecars/shared-volumes/shared/
ENV SHARED_DIR=/opt/palantir/sidecars/shared-volumes/shared

COPY --chmod=0755 entrypoint.py /usr/bin/entrypoint

# copy database from db_creator
COPY --chmod=700 --from=db_creator /pgdata /pgdata
RUN chown -R 5001:5001 /tmp /var/run/postgresql /pgdata
ARG state_var
RUN echo "$state_var" > /pgdata/states

WORKDIR /opt/palantir/sidecars/shared-volumes/shared/
USER 5001
ENTRYPOINT ["entrypoint", "-c", "/app/geocode"]

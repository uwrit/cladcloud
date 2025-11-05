# https://stackoverflow.com/questions/34751814/build-postgres-docker-container-with-initial-schema
# Initialize the database during the build
# PART 1
FROM postgis/postgis:17-3.5-alpine AS buildtime_init_builder

# build vars
ARG state_var
ARG TIGER_DOMAIN
ARG POSTGRES_DB=geocoder
ARG POSTGRES_USER=clad_svc
ARG POSTGRES_PASSWORD=not_on_gitlab
ARG GEOCODER_YEAR=2020

# runtime vars
ENV STATES=${state_var}
ENV TIGER_DOMAIN=${TIGER_DOMAIN}
ENV PGDATA=/pgdata

SHELL ["/bin/bash", "-c"]

RUN apk add libintl postgis unzip wget
# Make data dir
RUN mkdir -m 777 /gisdata
COPY ./src/alpinedb/download_national.sh .
COPY ./src/alpinedb/download_state.sh .
COPY ./src/alpinedb/1-load_data.sh /docker-entrypoint-initdb.d/
RUN echo "docker_temp_server_stop && exit 0" > /docker-entrypoint-initdb.d/900-exit_before_boot.sh

# download national data first
RUN ./download_national.sh
# force build to not use cache from a previous state(s) build:
ADD "https://www.random.org/cgi-bin/randbyte?nbytes=10&format=h" skipcache
# download state data in separate layer
RUN ./download_state.sh

RUN bash -x docker-entrypoint.sh postgres


# PART 2
## copy database from initialization layer
FROM alpine:latest AS buildtime_init
RUN apk upgrade --no-cache
## run apk to install key tools
RUN apk add bash libcurl postgis py3-pip py3-psycopg unzip vim wget

## image rebuild from scratch
CMD ["/bin/sh"]
#RUN /bin/sh -c set -eux; addgroup -g 70 -S postgres; adduser -u 70 -S -D -G postgres -H -h /var/lib/postgresql -s /bin/sh postgres; install --verbose --directory --owner postgres --group postgres --mode 1777 /var/lib/postgresql # buildkit
ENV LANG=en_US.utf8
ENV PG_MAJOR=16
ENV PG_VERSION=16.9
ENV PG_SHA256=07c00fb824df0a0c295f249f44691b86e3266753b380c96f633c3311e10bd005
ENV POSTGIS_VERSION=3.5.2
ENV POSTGIS_SHA256=71d8f5d06debec0bdd94525a5a1d42417ed2a1f65d0070a1a3e3e381b606ee35
ENV PGDATA=/pgdata_init

RUN /bin/sh -c set -eux; wget -O postgresql.tar.bz2 "https://ftp.postgresql.org/pub/source/v$PG_VERSION/postgresql-$PG_VERSION.tar.bz2"; echo "$PG_SHA256 *postgresql.tar.bz2" | sha256sum -c -; mkdir -p /usr/src/postgresql; tar --extract --file postgresql.tar.bz2 --directory /usr/src/postgresql --strip-components 1 ; rm postgresql.tar.bz2; apk add --no-cache --virtual .build-deps llvm15-dev clang15 bison coreutils dpkg-dev dpkg flex g++ gcc krb5-dev libc-dev libedit-dev libxml2-dev libxslt-dev linux-headers make openldap-dev openssl-dev perl-dev perl-ipc-run perl-utils python3-dev tcl-dev util-linux-dev zlib-dev icu-dev lz4-dev zstd-dev ; cd /usr/src/postgresql; awk '$1 == "#define" && $2 == "DEFAULT_PGSOCKET_DIR" && $3 == "\"/tmp\"" { $3 = "\"/var/run/postgresql\""; print; next } { print }' src/include/pg_config_manual.h > src/include/pg_config_manual.h.new; grep '/var/run/postgresql' src/include/pg_config_manual.h.new; mv src/include/pg_config_manual.h.new src/include/pg_config_manual.h; gnuArch="$(dpkg-architecture --query DEB_BUILD_GNU_TYPE)"; wget -O config/config.guess 'https://git.savannah.gnu.org/cgit/config.git/plain/config.guess?id=7d3d27baf8107b630586c962c057e22149653deb'; wget -O config/config.sub 'https://git.savannah.gnu.org/cgit/config.git/plain/config.sub?id=7d3d27baf8107b630586c962c057e22149653deb'; export LLVM_CONFIG="/usr/lib/llvm15/bin/llvm-config"; export CLANG=clang-15; ./configure --enable-option-checking=fatal --build="$gnuArch" --enable-integer-datetimes --enable-thread-safety --enable-tap-tests --disable-rpath --with-uuid=e2fs --with-pgport=5432 --with-system-tzdata=/usr/share/zoneinfo --prefix=/usr/local --with-includes=/usr/local/include --with-libraries=/usr/local/lib --with-gssapi --with-ldap --with-tcl --with-perl --with-python --with-openssl --with-libxml --with-libxslt --with-icu --with-llvm --with-lz4 --with-zstd ; make -j "$(nproc)" world-bin; make install-world-bin; make -C contrib install; runDeps="$( scanelf --needed --nobanner --format '%n#p' --recursive /usr/local | tr ',' '\n' | sort -u | awk 'system("[ -e /usr/local/lib/" $1 " ]") == 0 { next } { print "so:" $1 }' | grep -v -e perl -e python -e tcl )"; apk add --no-cache --virtual .postgresql-rundeps $runDeps bash tzdata zstd icu-data-full $([ "$(apk --print-arch)" != 'ppc64le' ] && echo 'nss_wrapper') ; apk del --no-network .build-deps; cd /; rm -rf /usr/src/postgresql /usr/local/share/doc /usr/local/share/man ; postgres --version # buildkit
RUN /bin/sh -c set -eux; cp -v /usr/local/share/postgresql/postgresql.conf.sample /usr/local/share/postgresql/postgresql.conf.sample.orig; sed -ri "s!^#?(listen_addresses)\s*=\s*\S+.*!\1 = '*'!" /usr/local/share/postgresql/postgresql.conf.sample; grep -F "listen_addresses = '*'" /usr/local/share/postgresql/postgresql.conf.sample # buildkit
RUN mkdir -m 777 /var/run/postgresql
RUN chown -R postgres:postgres /var/run/postgresql # buildkit
RUN mkdir -m 777 /pgdata_init
RUN chown -R postgres:postgres /pgdata_init # buildkit
CMD ["postgres"]
RUN /bin/sh -c set -eux && apk add --no-cache --virtual .fetch-deps ca-certificates openssl tar && wget -O postgis.tar.gz "https://github.com/postgis/postgis/archive/${POSTGIS_VERSION}.tar.gz" && echo "${POSTGIS_SHA256} *postgis.tar.gz" | sha256sum -c - && mkdir -p /usr/src/postgis && tar --extract --file postgis.tar.gz --directory /usr/src/postgis --strip-components 1 && rm postgis.tar.gz && apk add --no-cache --virtual .build-deps gdal-dev geos-dev proj-dev proj-util sfcgal-dev llvm15-dev clang15 autoconf automake cunit-dev file g++ gcc gettext-dev git json-c-dev libtool libxml2-dev make pcre2-dev perl protobuf-c-dev && cd /usr/src/postgis && gettextize && ./autogen.sh && ./configure --enable-lto && make -j$(nproc) && make install && projsync --system-directory --file ch_swisstopo_CHENyx06_ETRS && projsync --system-directory --file us_noaa_eshpgn && projsync --system-directory --file us_noaa_prvi && projsync --system-directory --file us_noaa_wmhpgn && mkdir /tempdb && chown -R postgres:postgres /tempdb && su postgres -c 'pg_ctl -D /tempdb init' && su postgres -c 'pg_ctl -D /tempdb -c -l /tmp/logfile -o '-F' start ' && cd regress && make -j$(nproc) check RUNTESTFLAGS=--extension PGUSER=postgres && su postgres -c 'psql -c "CREATE EXTENSION IF NOT EXISTS postgis;"' && su postgres -c 'psql -c "CREATE EXTENSION IF NOT EXISTS postgis_raster;"' && su postgres -c 'psql -c "CREATE EXTENSION IF NOT EXISTS postgis_sfcgal;"' && su postgres -c 'psql -c "CREATE EXTENSION IF NOT EXISTS fuzzystrmatch; --needed for postgis_tiger_geocoder "' && su postgres -c 'psql -c "CREATE EXTENSION IF NOT EXISTS address_standardizer;"' && su postgres -c 'psql -c "CREATE EXTENSION IF NOT EXISTS address_standardizer_data_us;"' && su postgres -c 'psql -c "CREATE EXTENSION IF NOT EXISTS postgis_tiger_geocoder;"' && su postgres -c 'psql -c "CREATE EXTENSION IF NOT EXISTS postgis_topology;"' && su postgres -c 'psql -t -c "SELECT version();"' >> /_pgis_full_version.txt && su postgres -c 'psql -t -c "SELECT PostGIS_Full_Version();"' >> /_pgis_full_version.txt && su postgres -c 'psql -t -c "\dx"' >> /_pgis_full_version.txt && su postgres -c 'pg_ctl -D /tempdb --mode=immediate stop' && rm -rf /tempdb && rm -rf /tmp/logfile && rm -rf /tmp/pgis_reg && apk add --no-cache --virtual .postgis-rundeps gdal geos proj sfcgal json-c libstdc++ pcre2 protobuf-c ca-certificates && cd / && rm -rf /usr/src/postgis && apk del .fetch-deps .build-deps && cat /_pgis_full_version.txt # buildkit
## image rebuild end

SHELL ["/bin/bash", "-c"]

# Foundry customizations
RUN adduser --uid 5001 --disabled-password user
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

RUN mkdir -m 700 /pgdata
RUN chown 5001:5001 /pgdata
COPY --chown=5001:5001 --chmod=700 --from=buildtime_init_builder /pgdata /pgdata
ENV PGDATA=/pgdata

USER 5001
ENTRYPOINT entrypoint -c "/foundry_venv/bin/python3 /process_csv.py"

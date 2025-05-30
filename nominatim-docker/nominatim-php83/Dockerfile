ARG NOMINATIM_VERSION=4.4.0
ARG USER_AGENT=mediagis/nominatim-docker:${NOMINATIM_VERSION}

FROM ubuntu:noble AS build

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

WORKDIR /app

# update base first
RUN apt -y update -qq \
    && apt -y dist-upgrade

# Inspired by https://github.com/reproducible-containers/buildkit-cache-dance?tab=readme-ov-file#apt-get-github-actions
RUN  \
    --mount=type=cache,target=/var/cache/apt,sharing=locked \
    --mount=type=cache,target=/var/lib/apt,sharing=locked \
    # Keep downloaded APT packages in the docker build cache
    rm -f /etc/apt/apt.conf.d/docker-clean && \
    echo 'Binary::apt::APT::Keep-Downloaded-Packages "true";' >/etc/apt/apt.conf.d/keep-cache && \
    # Do not start daemons after installation.
    echo '#!/bin/sh\nexit 101' > /usr/sbin/policy-rc.d \
    && chmod +x /usr/sbin/policy-rc.d \
    # Install all required packages.
    && apt -y update -qq \
    && apt -y install \
        locales \
    && locale-gen en_US.UTF-8 \
    && update-locale LANG=en_US.UTF-8 \
    && apt -y install \
        -o APT::Install-Recommends="false" \
        -o APT::Install-Suggests="false" \
        # Build tools from sources.
        build-essential \
        cmake \
        libpq-dev \
        zlib1g-dev \
        libbz2-dev \
        libproj-dev \
        libexpat1-dev \
        libboost-dev \
        libboost-system-dev \
        libboost-filesystem-dev \
        liblua5.4-dev \
        nlohmann-json3-dev \
        # PostgreSQL.
        postgresql-contrib \
        postgresql-server-dev-16 \
        postgresql-16-postgis-3 \
        postgresql-16-postgis-3-scripts \
        # PHP and Apache 2.
        php \
        php-intl \
        php-pgsql \
        php-cgi \
        apache2 \
        libapache2-mod-php \
        # Python 3.
        python3-dev \
        python3-pip \
        python3-tidylib \
        python3-psycopg2 \
        python3-setuptools \
        python3-dotenv \
        python3-psutil \
        python3-jinja2 \
        python3-sqlalchemy \
        python3-asyncpg \
        python3-datrie \
        python3-icu \
        python3-argparse-manpage \
        # Misc.
        git \
        curl \
        sudo \
        sshpass \
        openssh-client


# Configure postgres.
RUN true \
    && echo "host all all 0.0.0.0/0 md5" >> /etc/postgresql/16/main/pg_hba.conf \
    && echo "listen_addresses='*'" >> /etc/postgresql/16/main/postgresql.conf

# Osmium install to run continuous updates.
#RUN --mount=type=cache,target=/root/.cache/pip,sharing=locked \
#    pip3 install osmium

# Nominatim install.
ARG NOMINATIM_VERSION
ARG USER_AGENT

RUN true \
    && curl -A $USER_AGENT https://nominatim.org/release/Nominatim-$NOMINATIM_VERSION.tar.bz2 -o nominatim.tar.bz2 \
    && tar xf nominatim.tar.bz2 \
    && mkdir build \
    && cd build \
    && cmake ../Nominatim-$NOMINATIM_VERSION \
    && make -j`nproc` \
    && make install

RUN true \
    # Remove development and unused packages.
    && apt-get -y remove --purge --auto-remove \
        build-essential \
        cmake \
        git \
        llvm-10* \
        linux-libc-dev \
        libclang-*-dev \
        liblua*-dev \
        nlohmann-json3-dev \
    # Clear temporary files and directories.
    && rm -rf \
        /tmp/* \
        /var/tmp/* \
        /app/src/.git \
    # Remove nominatim source and build directories
    && rm /app/*.tar.bz2 \
    && rm -rf /app/build \
    && rm -rf /app/Nominatim-$NOMINATIM_VERSION

# Apache configuration
COPY conf.d/apache.conf /etc/apache2/sites-enabled/000-default.conf

# Postgres config overrides to improve import performance (but reduce crash recovery safety)
COPY conf.d/postgres-import.conf /etc/postgresql/16/main/conf.d/postgres-import.conf.disabled
COPY conf.d/postgres-tuning.conf /etc/postgresql/16/main/conf.d/

COPY config.sh /app/config.sh
COPY init.sh /app/init.sh
COPY start.sh /app/start.sh
COPY startapache.sh /app/startapache.sh
COPY startpostgres.sh /app/startpostgres.sh

# Collapse image to single layer.
FROM scratch

COPY --from=build / /

# Please override this
ENV NOMINATIM_PASSWORD=notongitlab

ENV PROJECT_DIR=/nominatim

ARG USER_AGENT
ENV USER_AGENT=${USER_AGENT}

WORKDIR /app

EXPOSE 5432
EXPOSE 8080

COPY conf.d/env $PROJECT_DIR/.env

CMD ["/app/start.sh"]

# remove bad key
RUN rm -rf /etc/ssl/private/ssl-cert-snakeoil.key

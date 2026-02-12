FROM debian:trixie-20260202-slim AS builder

RUN apt-get update && apt-get install -y \
    make \
    sqlite3 \
    libsqlite3-dev \
    flex \
    bison \
    pkg-config \
    ruby \
    ruby-dev \
    git \
    && apt-get clean

RUN gem install sqlite3 json Text

WORKDIR /build

RUN git clone https://github.com/beusj/geocoder.git

WORKDIR /build/geocoder

# remove existing build files
RUN rm -rf /build/build

# NOTE: CFLAGS reduces complier strictness to that of ruby 2.x
RUN CFLAGS="-Wno-implicit-function-declaration" make -f Makefile.ruby install \
    && gem install Geocoder-US-2.0.4.gem


FROM ruby:4.0-alpine AS runtime
COPY --from=builder /var/lib/gems/3.3.0/gems /usr/local/lib/ruby/gems/4.0.0/gems
COPY --from=builder /build/geocoder/geocode.rb /app/geocode.rb
COPY --from=ghcr.io/astral-sh/uv:0.10.2 /uv /uvx /bin/

ARG PYTHON_VERSION=3.14
RUN uv python install ${PYTHON_VERSION}
RUN export PATH=$PATH:/root/.local/bin

# TODO: change this to clad-builder VM
ARG GEOCODER_LOCATION=http://clad-github-builder.rit.uw.edu/geo/geocoder-2021.gb
ADD ${GEOCODER_LOCATION} /opt/geocoder.db

# FIX: this sucks just to use `-S` in our `uv` shebang
RUN apk add --no-cache coreutils bash

WORKDIR /app

COPY --chmod=0755 ./process_csv.py .
COPY --chmod=0755 ./entrypoint.py .

RUN adduser --uid 5001 --disabled-password user

ARG SHARED_DIR=/opt/palantir/sidecars/shared-volumes/shared

RUN mkdir -p ${SHARED_DIR}

RUN chown -R 5001:5001 /app /opt

USER 5001

ENTRYPOINT ["bash"]

# ENTRYPOINT ["/app/entrypoint.py", "-c", "/app/process_csv.py"]

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

# checkout specific hash - Jan 5, 2025
RUN git checkout 13074b42d2a8f13d7d6d3b2c1a540b5fc7e25f65

# remove existing build files
RUN rm -rf /build/build

# NOTE: CFLAGS reduces complier strictness to that of ruby 2.x
RUN CFLAGS="-Wno-implicit-function-declaration" make -f Makefile.ruby install


FROM ruby:4.0-alpine AS runtime
COPY --from=builder /build/geocoder/Geocoder-US-2.0.4.gem /app/Geocoder-US-2.0.4.gem
COPY --from=builder /build/geocoder/geocode.rb /app/geocode.rb
COPY --from=ghcr.io/astral-sh/uv:0.10.2 /uv /uvx /bin/

ARG PYTHON_VERSION=3.14

ARG GEOCODER_LOCATION=http://clad-github-builder.rit.uw.edu/geo/geocoder-2021.gb
ADD ${GEOCODER_LOCATION} /opt/geocoder.db

# FIX: needing coreutils sucks just to use `-S` in our `uv` shebang
RUN apk add --no-cache \
    coreutils \
    sqlite-dev

WORKDIR /app

RUN gem install Geocoder-US-2.0.4.gem

COPY --chmod=0755 ./process_csv.py .
COPY --chmod=0755 ./entrypoint.py .

RUN adduser --uid 5001 --disabled-password user

ARG SHARED_DIR=/opt/palantir/sidecars/shared-volumes/shared

RUN mkdir -p ${SHARED_DIR}

RUN chown -R 5001:5001 /app /opt

USER 5001

# install python as correct user and add user python binary to path
RUN uv python install ${PYTHON_VERSION}
RUN export PATH=$PATH:/home/user/.local/bin

ENTRYPOINT ["/app/entrypoint.py", "-c", "/app/process_csv.py"]

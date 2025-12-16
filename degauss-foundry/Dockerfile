FROM rocker/r-ver:4.5.1 AS compiler

RUN apt-get update && apt-get install -y \
    bison \
    flex \
    gnupg \
    libcurl4-openssl-dev \
    libsqlite3-dev \
    libssh2-1-dev \
    libssl-dev \
    libxml2-dev \
    make \
    pkg-config \
    ruby-full \
    sqlite3 \
    wget \
    make \
    git \
    software-properties-common
RUN gem install sqlite3 json Text
RUN apt-get dist-upgrade -yq

WORKDIR /app
RUN git clone https://github.com/degauss-org/geocoder
WORKDIR /app/geocoder
# NOTE: switch to latest known commit
RUN git checkout 9fab80e
# remove existing build dir
RUN rm -rf build

RUN make -f Makefile.ruby install

FROM ruby:3.4-alpine
COPY --from=ghcr.io/astral-sh/uv:0.9.17 /uv /uvx /bin/
COPY --from=compiler /app/geocoder/Geocoder-US-2.0.4.gem /app/Geocoder-US-2.0.4.gem
COPY --from=compiler /app/geocoder/geocode.rb /app/geocode.rb

ENV SHARED_DIR=/opt/palantir/sidecars/shared-volumes/shared

WORKDIR /app
COPY entrypoint.py .
COPY main.py .
COPY main.py.lock .

ADD http://clad-github-builder.rit.uw.edu/geo/geocoder-2021.db /opt/geocoder.db

RUN gem install Geocoder-US-2.0.4.gem

RUN uv sync --locked --script /app/main.py

RUN apk update && apk upgrade --no-cache
RUN apk add --no-cache sqlite

RUN adduser --uid 5001 --disabled-password user

RUN chown -R 5001:5001 /app /opt

USER 5001

ENTRYPOINT ["uv", "run", "-q", "--script", "/app/entrypoint.py", "-c", "uv run -q --script /app/main.py"]

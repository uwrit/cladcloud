FROM postgis/postgis:18-3.6 AS builder

ARG STATE
ARG YEAR
ARG DOMAIN
ARG POSTGRES_DB=geocoder

# expose args as env vars
ENV DOMAIN=${DOMAIN}
ENV STATE=${STATE}
ENV YEAR=${YEAR}
ENV PGDATA=/pgdata

RUN apt-get update && apt-get upgrade

RUN apt-get install -y \
  wget \
  unzip \
  postgis

COPY sql /app/sql
COPY scripts/*.sh /app/scripts/
RUN chmod +x /app/scripts/*.sh

# give postgres user access to gisdata (from sql scripts)
# and pgdata
RUN mkdir -p /gisdata \
  && chown -R postgres:postgres /gisdata \
  && chmod -R 755 /gisdata
RUN mkdir -p "${PGDATA}" \
  && chown -R postgres:postgres "${PGDATA}" \
  && chmod -R 755 "${PGDATA}"


# BUG: this was needed for some reason w/ certs on clad-github-builder.rit.uw.edu
RUN printf "check_certificate = off\n" >> /etc/wgetrc

USER postgres 
RUN initdb -D "$PGDATA"

# start postgres, create db, seed it, and close postgres
# NOTE: must be in one "docker" command
RUN pg_ctl -D "$PGDATA" -o "-c listen_addresses='localhost'" -w start \
  && createdb -O postgres geocoder \
  && psql -d $POSTGRES_DB -f /app/sql/schemas.sql \
  && psql -d $POSTGRES_DB -f /app/sql/extensions.sql \
  && /app/scripts/automated.sh \
  && pg_ctl -D "$PGDATA" -m fast stop


# main stage
FROM postgis/postgis:18-3.6-alpine
COPY --from=ghcr.io/astral-sh/uv:0.9.17 /uv /uvx /bin/
COPY --from=builder /pgdata /pgdata

ENV PGDATA=/pgdata
ENV POSTGRES_DB=geocoder
ENV POSTGRES_PASSWORD=unchecked
# used as volume, env var read by python csv processor
ENV SHARED_DIR=/opt/palantir/sidecars/shared-volumes/shared

RUN apk update && apk upgrade --no-cache

RUN adduser --uid 5001 --disabled-password user

WORKDIR /app

# give runtime user access to /app
RUN mkdir -p "${PGDATA}" \
  && chown -R 5001:5001 "${PGDATA}" \
  && chmod -R 700 "${PGDATA}"
RUN chown -R 5001:5001 /app
RUN chown -R 5001:5001 /tmp /pgdata

COPY scripts/main.py /app/main.py
COPY scripts/main.py.lock /app/main.py.lock
COPY scripts/entrypoint.py /app/entrypoint.py

RUN uv sync --locked --script /app/main.py

USER 5001

# actually initialize
RUN pg_ctl -D "$PGDATA" -o "-c listen_addresses='localhost'" -w start \
  && pg_ctl -D "$PGDATA" -m fast stop


ENTRYPOINT ["uv", "run", "-q", "--script", "/app/entrypoint.py", "-c", "uv run -q --script /app/main.py"]


FROM postgis/postgis:18-3.6
COPY --from=ghcr.io/astral-sh/uv:0.9.17 /uv /uvx /bin/

ARG STATE
ARG YEAR
ARG DOMAIN
ARG POSTGRES_DB=geocoder

# expose args as env vars
ENV DOMAIN=${DOMAIN}
ENV STATE=${STATE}
ENV YEAR=${YEAR}
ENV PGDATA=/pgdata
# used as volume, env var read by python csv processor
ENV SHARED_DIR=/opt/palantir/sidecars/shared-volumes/shared

RUN adduser --uid 5001 --disabled-password user

RUN apt-get update && apt-get upgrade

RUN apt-get install -y \
  wget \
  unzip \
  postgis

COPY sql /app/sql
COPY scripts/*.sh /app/scripts/
RUN chmod +x /app/scripts/*.sh

# give runtime user access to /app
RUN chown -R 5001:5001 /app \
  && chmod -R 755 /app

# give postgres user access to gisdata (from sql scripts)
# and pgdata
RUN mkdir -p /gisdata \
  && chown -R postgres:postgres /gisdata \
  && chmod -R 755 /gisdata
RUN mkdir -p "${PGDATA}" \
  && chown -R postgres:postgres "${PGDATA}" \
  && chmod -R 755 "${PGDATA}"
RUN mkdir -p "${PGDATA}" \
  && chown -R 5001:5001 "${PGDATA}" \
  && chmod -R 755 "${PGDATA}"

COPY scripts/main.py /app/main.py
COPY scripts/main.py.lock /app/main.py.lock
COPY scripts/entrypoint.py /app/entrypoint.py
RUN chmod +x /app/main.py
RUN chmod +x /app/entrypoint.py

# BUG: this was needed for some reason w/ certs on clad-github-builder.rit.uw.edu
RUN printf "check_certificate = off\n" >> /etc/wgetrc

RUN uv sync --locked --script /app/main.py

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

USER 5001

ENTRYPOINT ["uv", "run", "-q", "--script", "/app/entrypoint.py", "-c", "uv run -q --script /app/main.py"]


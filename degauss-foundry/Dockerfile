# https://stackoverflow.com/questions/34751814/build-postgres-docker-container-with-initial-schema
# compile the gem for the build
# PART 1
FROM rocker/r-ver:4.4.1

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
    software-properties-common

RUN gem install sqlite3 json Text

RUN mkdir /app
WORKDIR /app

COPY Makefile.ruby .
COPY /src ./src
COPY /lib ./lib
COPY /gemspec ./gemspec

RUN make -f Makefile.ruby install 


# PART 2
## copy build from initialization layer
FROM rhub/r-minimal:4.5.0 AS buildtime_init

# DeGAUSS container metadata
ENV degauss_name="geocoder"
ENV degauss_version="3.4.0"
ENV degauss_description="geocodes"
ENV degauss_argument="valid_geocode_score_threshold [default: 0.5]"

# add OCI labels based on environment variables too
LABEL "org.degauss.name"="${degauss_name}"
LABEL "org.degauss.version"="${degauss_version}"
LABEL "org.degauss.description"="${degauss_description}"
LABEL "org.degauss.argument"="${degauss_argument}"

RUN mkdir /app
WORKDIR /app

COPY --from=buildtime_init_builder Geocoder-US-2.0.4.gem Geocoder-US-2.0.4.gem
ADD https://colebrokamp-dropbox.s3.amazonaws.com/geocoder.db /opt/geocoder.db

RUN apk add \
    bison \
    flex \
    g++ \
    gcc \
    gnupg \
    linux-headers \
    musl-dev \
    py3-pip \
    ruby \
    sqlite \
    vim
RUN apk upgrade --no-cache

RUN gem install json sqlite3 Text
RUN gem install Geocoder-US-2.0.4.gem

# install required version of renv
RUN R --quiet -e "install.packages('remotes', repos = c(CRAN = 'https://packagemanager.posit.co/cran/latest'))"
RUN R --quiet -e "remotes::install_github('rstudio/renv@v1.0.7')"

COPY renv.lock .
RUN R --quiet -e "renv::restore(repos = c(CRAN = 'https://packagemanager.posit.co/cran/latest'))"

COPY entrypoint.R .
COPY geocode.rb .

# Foundry customizations part 1
RUN adduser --uid 5001 --disabled-password user
RUN chown -R 5001:5001 /tmp /opt /app

# Foundry customizations pt2
# RUN adduser --uid 5001 --disabled-password user
# RUN chown -R 5001:5001 /tmp /opt /app

ADD entrypoint.py /usr/bin/entrypoint
RUN chmod +x /usr/bin/entrypoint
RUN mkdir -p /opt/palantir/sidecars/shared-volumes/shared/
RUN chown 5001 /opt/palantir/sidecars/shared-volumes/shared/
ENV SHARED_DIR=/opt/palantir/sidecars/shared-volumes/shared

USER 5001
WORKDIR /opt/palantir/sidecars/shared-volumes/shared/
ENTRYPOINT entrypoint -c "/app/entrypoint.R /opt/palantir/sidecars/shared-volumes/shared/infile.csv all"

FROM rhub/r-minimal:latest

# DeGAUSS container metadata
ENV degauss_name="geocoder"
ENV degauss_version="3.3.0"
ENV degauss_description="geocodes"
ENV degauss_argument="valid_geocode_score_threshold [default: 0.5]"

# add OCI labels based on environment variables too
LABEL "org.degauss.name"="${degauss_name}"
LABEL "org.degauss.version"="${degauss_version}"
LABEL "org.degauss.description"="${degauss_description}"
LABEL "org.degauss.argument"="${degauss_argument}"

RUN apk add \
    make \
    sqlite \
    sqlite-dev \
    sqlite-libs \
    flex \
    ruby-full \
    ruby-dev \
    bison \
    gnupg \
    gcc \
    g++ \
    musl-dev \
    python3 \
    py3-pip \
    vim \
    linux-headers

RUN gem install sqlite3 
RUN gem install json Text

RUN apk upgrade --no-cache

RUN mkdir /app
WORKDIR /app




COPY Makefile.ruby .
COPY /src ./src
COPY /lib ./lib
COPY /gemspec ./gemspec

RUN make -f Makefile.ruby install \
    && gem install Geocoder-US-2.0.4.gem

WORKDIR /app

# install required version of renv
RUN R --quiet -e "install.packages('remotes', repos = 'https://packagemanager.rstudio.com/all/__linux__/focal/latest')"
RUN R --quiet -e "remotes::install_github('rstudio/renv@0.15.5')"

COPY renv.lock .
RUN R --quiet -e "renv::restore()"

COPY entrypointCSV.R .
COPY geocode.rb .

ADD https://geomarker.s3.amazonaws.com/geocoder_2021.db /opt/geocoder.db

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

ENTRYPOINT entrypoint -c "/app/entrypointCSV.R /opt/palantir/sidecars/shared-volumes/shared/infile.csv all"

FROM rhub/r-minimal:4.5.0
RUN apk upgrade --no-cache

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
    bison \
    flex \
    g++ \
    gcc \
    gnupg \
    linux-headers \
    make \
    musl-dev \
    sqlite \
    sqlite-dev \
    sqlite-libs \
    ruby-dev \
    ruby-full \
    python3 \
    py3-pip \
    vim

RUN gem install sqlite3 
RUN gem install json Text

RUN mkdir /app
WORKDIR /app

COPY Makefile.ruby .
COPY /src ./src
COPY /lib ./lib
COPY /gemspec ./gemspec

RUN make -f Makefile.ruby install \
    && gem install Geocoder-US-2.0.4.gem

# install required version of renv
RUN R --quiet -e "install.packages('remotes', repos = 'https://packagemanager.rstudio.com/all/__linux__/focal/latest')"
RUN R --quiet -e "remotes::install_github('rstudio/renv')"

COPY renv.lock .
RUN R --quiet -e "renv::restore()"

ADD https://colebrokamp-dropbox.s3.amazonaws.com/geocoder.db /opt/geocoder.db

# Foundry customizations
COPY entrypointCSV.R .
COPY geocode.rb .

ADD entrypoint.py /usr/bin/entrypoint
RUN chmod +x /usr/bin/entrypoint

RUN mkdir -p /opt/palantir/sidecars/shared-volumes/shared
RUN adduser --uid 5001 --disabled-password user
RUN chown -R 5001:5001 /tmp /opt /app
RUN chown 5001 /opt/palantir/sidecars/shared-volumes/shared
ENV SHARED_DIR=/opt/palantir/sidecars/shared-volumes/shared

USER 5001
WORKDIR /opt/palantir/sidecars/shared-volumes/shared

ENTRYPOINT entrypoint -c "/app/entrypointCSV.R /opt/palantir/sidecars/shared-volumes/shared/infile.csv all"

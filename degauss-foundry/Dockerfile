# https://stackoverflow.com/questions/34751814/build-postgres-docker-container-with-initial-schema
# compile the gem for the build
# PART 1
FROM rocker/r-ver AS compiler

# copy statics
RUN mkdir /app
WORKDIR /app
COPY Makefile.ruby .
COPY /src ./src
COPY /lib ./lib
COPY /gemspec ./gemspec

# install dependencies
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
RUN apt-get dist-upgrade -yq

# build gem
RUN make -f Makefile.ruby install


# PART 2
## ADD build from initialization layer
FROM rhub/r-minimal

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

# copy statics
RUN mkdir /app
WORKDIR /app
COPY --from=compiler /app/Geocoder-US-2.0.4.gem Geocoder-US-2.0.4.gem
ADD https://colebrokamp-dropbox.s3.amazonaws.com/geocoder.db /opt/geocoder.db
COPY entrypoint.R .
COPY geocode.rb .

# install entrypoint.R dependencies
RUN apk add py3-pip ruby
RUN gem install Geocoder-US-2.0.4.gem
RUN R --quiet -e "install.packages(c('digest','knitr','mappp','remotes'), repos=c(CRAN='https://packagemanager.posit.co/cran/latest'))"
RUN R --quiet -e "remotes::install_github('degauss-org/dht')"
RUN apk upgrade --no-cache

# Foundry customizations
COPY --chmod=0755 entrypoint.py /usr/bin/entrypoint
RUN adduser --uid 5001 --disabled-password user
RUN chown -R 5001:5001 /tmp /app

RUN mkdir -p /opt/palantir/sidecars/shared-volumes/shared/
RUN chown -R 5001:5001 /opt
ENV SHARED_DIR=/opt/palantir/sidecars/shared-volumes/shared

USER 5001
WORKDIR /opt/palantir/sidecars/shared-volumes/shared/
ENTRYPOINT entrypoint -c "/app/entrypoint.R /opt/palantir/sidecars/shared-volumes/shared/infile.csv all"

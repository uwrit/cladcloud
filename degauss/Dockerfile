# PART 1 - https://stackoverflow.com/questions/34751814/build-postgres-docker-container-with-initial-schema
# compile the gem for the build
FROM rocker/r-ver AS compile-gem

# copy statics
RUN mkdir /app
WORKDIR /app
COPY Makefile.ruby .
COPY /src ./src
COPY /lib ./lib
COPY /gemspec ./gemspec

# install dependencies
RUN apt-get update && apt-get dist-upgrade -yq && apt-get install -y \
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
    software-properties-common \
    sqlite3
# default to not documenting ruby installs - speeds up build
RUN echo "gem: --no-document" > ~/.gemrc
RUN gem update && \
    gem install sqlite3 json Text && \
    rm -f /usr/lib/ruby/gems/3.4.0/specifications/sqlite3-ruby-1.3.3.gemspec

# build gem
RUN make -f Makefile.ruby install


# PART 2
# ADD build from initialization layer
FROM rhub/r-minimal as r-dirty

# copy statics
RUN mkdir /app
WORKDIR /app
COPY --chmod=755 geocode.R /app/geocode
COPY geocode.rb .
ADD http://clad-github-builder.rit.uw.edu/geo/geocoder-2021.db /app/geocoder.db
RUN echo "gem: --no-document" > ~/.gemrc

# first update alpine (r-minimal is currently based on old 3.22, 3.24 is current as of 2026-09-17 and alpine has no automatic version upgrade tool)
RUN sed -i 's|v3\.[0-9]*|v3.24|g' /etc/apk/repositories
# upgrade apk first
RUN apk add --no-cache --upgrade apk-tools
# then upgrade the system
RUN apk --no-cache upgrade
# add packages needed for degauss geocoder and palantir (ruby, R, and python)
RUN apk --no-cache add py3-pip ruby build-base linux-headers
# pip install shortcut - pipi
RUN echo -e '#!/bin/bash\nexec python3 -m pip install --break-system-packages --no-cache-dir --ignore-installed "$@"' > /usr/local/bin/pipi && \
    chmod +x /usr/local/bin/pipi
# upgrade pip first
RUN pipi --upgrade pip
# then upgrade the rest of python
RUN python3 -m pip freeze --all | sed 's/==/>=/g' | xargs pipi --upgrade
# install entrypoint.R R dependencies
RUN installr -d degauss-org/dht digest docopt jsonlite knitr mappp

# finally install needed packages
COPY --from=compile-gem /app/Geocoder-US-2.0.4.gem /tmp/Geocoder-US-2.0.4.gem
RUN gem install /tmp/Geocoder-US-2.0.4.gem
# force upgrade of ruby dependency packages installed from previous command
RUN gem update --system --force && gem update

# ADDRESS CVEs:
# drop old tracking stubs that package managers refused to overwrite - eliminates all vulnerable paths caught in Trivy scans
RUN find /usr/lib/python* -type d \( \
    -name "*license*" -o \
    -name "msgpack-1.1.2*" -o \
    -name "pip-26.1.2*" -o \
    -name "setuptools-70.3.0*" -o \
    \) -exec rm -rf {} +
RUN rm -rf /usr/lib/python*/ensurepip \
    /usr/lib/python*/site-packages/msgpack*/_vendor \
    /usr/lib/python*/site-packages/pip*/_vendor/msgpack* \
    /usr/lib/python*/site-packages/pip*/_vendor/setuptools* \
    /usr/lib/python*/site-packages/pkg_resources*/_vendor \
    /usr/lib/python*/site-packages/setuptools*/_vendor
# remove all references to deleted python binaries
RUN find /usr/lib/python* \( \
    -iname "*.json" -o \
    -iname "*.txt" -o \
    -iname "*.whl" -o \
    \) -delete
# remove old ruby libraries
RUN rm -rf /usr/lib/ruby/gems/*/specifications/default/erb-* \
    /usr/lib/ruby/gems/*/specifications/default/json-* \
    /usr/lib/ruby/gems/*/specifications/default/resolv-* \
    /usr/lib/ruby/gems/*/specifications/default/uri-* \
    /usr/lib/ruby/gems/*/specifications/default/zlib-* \
    /usr/lib/ruby/gems/*/specifications/sqlite3-ruby-1.3.*

# strip all language-specific test suites, examples, and non-functional docs
RUN find /usr/lib/python* /usr/lib/ruby -type d \( \
    -name "test" -o \
    -name "tests" -o \
    -name "idlelib" -o \
    -name "turtledemo" -o \
    -name "examples" -o \
    -name "doc" -o \
    -name "docs" -o \
    \) -exec rm -rf {} +
# strip broad system-level documentation, localized manual pages, and help guides
RUN rm -rf /usr/share/man \
    /usr/share/doc \
    /usr/share/info \
    /usr/share/gtk-doc \
    /usr/share/help/* \
    /usr/lib/ruby/gems/*/doc/*
# strip C/C++ development header artifacts (.h files)
RUN find /usr/include /usr/lib/python* -name "*.h" -delete
# strip all python bytecode translation caches (__pycache__)
RUN find /usr/lib/python* -name "__pycache__" -type d -exec rm -rf {} +
# strip fallback package indexing database binaries left by apk and pip
RUN rm -rf /var/cache/apk/* \
    /lib/apk/db/scripts.tar \
    /root/.cache \
    /root/.cargo


# PART 3 - The Ultimate Clean Runtime Stage
# --squash is deprecated, --output squash=true is broken, COPY --from=dirty / / copies all layer junk (deleted files) as well, tar export/import doubles output container size, so copy main folders individually from previous step to get JUST the files and NOTHING from the deleted layers
FROM scratch as degauss

COPY --from=r-dirty /app /app
COPY --from=r-dirty /bin /bin
COPY --from=r-dirty /etc /etc
COPY --from=r-dirty /lib /lib
COPY --from=r-dirty /usr /usr
RUN mkdir -m 777 /tmp

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

# Foundry customizations
COPY --chmod=0755 entrypoint.py /usr/bin/entrypoint
RUN adduser --uid 5001 --disabled-password user
RUN mkdir -p /opt/palantir/sidecars/shared-volumes/shared/
RUN chown -R 5001:5001 /app /opt /tmp

USER 5001
ENV SHARED_DIR=/opt/palantir/sidecars/shared-volumes/shared
WORKDIR /opt/palantir/sidecars/shared-volumes/shared/
ENTRYPOINT ["entrypoint", "-c", "/app/geocode /opt/palantir/sidecars/shared-volumes/shared/infile.csv"]

FROM rhub/r-minimal:4.3.0

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
    py3-setuptools \
    vim \
    linux-headers

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

WORKDIR /app

# install required version of renv
RUN R --quiet -e "install.packages('remotes', repos = 'https://packagemanager.rstudio.com/all/__linux__/focal/latest')"
RUN R --quiet -e "remotes::install_github('rstudio/renv@0.15.4')"

COPY renv.lock .
RUN R --quiet -e "renv::restore()"

COPY geocode.rb .

ADD https://geomarker.s3.amazonaws.com/geocoder_2021.db /opt/geocoder.db

## api customizations

COPY requirements.txt ./
RUN pip3 install --no-cache-dir -r requirements.txt

COPY __init__.py ./
COPY manage.py ./
COPY /flaskr ./flaskr


WORKDIR /tmp

CMD [ "python3", "/app/manage.py" ]

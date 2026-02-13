#!/bin/bash

# set defaults
[[ -z ${DOMAIN} ]] && DOMAIN="www2.census.gov"
[[ -z ${GISDATA} ]] && GISDATA="/gisdata"
[[ -z ${POSTGRES_DB} ]] && POSTGRES_DB="geocoder"
[[ -z ${POSTGRES_PASSWORD} ]] && POSTGRES_PASSWORD="not_on_gitlab"
[[ -z ${POSTGRES_USER} ]] && POSTGRES_USER="postgres"
[[ -z ${STATES} ]] && STATES="AL,AK,AZ,AR,CA,CO,CT,DE,FL,GA,HI,ID,IL,IN,IA,KS,KY,LA,ME,MD,MA,MI,MN,MS,MO,MT,NE,NV,NH,NJ,NM,NY,NC,ND,OH,OK,OR,PA,RI,SC,SD,TN,TX,UT,VT,VA,WA,WV,WI,WY"
[[ -z ${YEAR} ]] && YEAR="2020"

while getopts "d:s:t:y:?" arg; do
    case ${arg} in
        d)  DOMAIN=${OPTARG} ;;
        s)  STATES=${OPTARG} ;;
        y)  YEAR=${OPTARG} ;;
        ?)  echo "Usage: "${0}' [-d domain] [-s "state[, state...]"] [-y year]' && exit 1 ;;
    esac
done

[[ -z ${BASEPATH} ]] && BASEPATH="${DOMAIN}/geo/tiger/TIGER${YEAR}"
[[ -z ${BASEURL} ]] && BASEURL="http://${BASEPATH}"

PSQL="psql -U $POSTGRES_USER -d ${POSTGRES_DB} -A -t -c "
SHP2PGSQL=shp2pgsql

echo '----------------------------------------'
echo ${BASEURL}" + "${STATES}
echo '----------------------------------------'

echo "      Loading extensions"
${PSQL} "
CREATE SCHEMA IF NOT EXISTS tiger_data;
CREATE EXTENSION IF NOT EXISTS postgis;
CREATE EXTENSION IF NOT EXISTS fuzzystrmatch;
CREATE EXTENSION IF NOT EXISTS postgis_tiger_geocoder;
CREATE EXTENSION IF NOT EXISTS address_standardizer;
UPDATE tiger.loader_lookuptables SET load = true WHERE load = false AND lookup_name IN('tract', 'bg', 'tabblock20');
"

fix_and_run() {
    sed -i '/^export PGHOST=/d' $1
    sed -i '/^export PGPORT=/d' $1
    sed -i 's/^PSQL=.*/PSQL=psql/' $1
    sed -i "s/www2\.census\.gov/$DOMAIN/g" $1
    sed -i "s/2024/$YEAR/g" $1
    sed -i "s/2025/$YEAR/g" $1
    bash -x $1
}

echo "      Loading national"
${PSQL} "SELECT loader_generate_nation_script('sh');" > ${GISDATA}/data_load.sh
fix_and_run ${GISDATA}/data_load.sh

# For each selected state
IFS=',' read -ra GEO_STATES <<< "${STATES^^}"
for state in "${GEO_STATES[@]}";
do
    echo "      Loading '$state' state data"
    ${PSQL} "SELECT loader_generate_script(ARRAY['${state}'], 'sh');" > ${GISDATA}/data_load.sh
    fix_and_run ${GISDATA}/data_load.sh

    # not needed since postgis 2.0.0
    # ${PSQL} "SELECT loader_generate_census_script(ARRAY['${state}'], 'sh');" ${GISDATA}/data_load.sh
    # fix_and_run ${GISDATA}/data_load.sh
done

${PSQL} "SELECT install_missing_indexes();"
vacuumdb -U $POSTGRES_USER -d ${POSTGRES_DB} -z -j $(nproc)

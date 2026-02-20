#!/bin/bash

# set defaults
[[ -z ${DOMAIN} ]] && DOMAIN="www2.census.gov"
[[ -z ${GISDATA} ]] && GISDATA="/gisdata"
[[ -z ${POSTGRES_DB} ]] && POSTGRES_DB="geocoder"
[[ -z ${POSTGRES_PASSWORD} ]] && POSTGRES_PASSWORD="not_on_gitlab"
[[ -z ${POSTGRES_USER} ]] && POSTGRES_USER="postgres"
[[ -z ${STATES} ]] && STATES="AK,AL,AR,AS,AZ,CA,CO,CT,DC,DE,FL,FM,GA,GU,HI,IA,ID,IL,IN,KS,KY,LA,MA,MD,ME,MH,MI,MN,MO,MS,MT,NC,ND,NE,NH,NJ,NM,NV,NY,OH,OK,OR,PA,PR,PW,RI,SC,SD,TN,TX,UT,VA,VI,VT,WA,WI,WV,WY"
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
UPDATE tiger.loader_lookuptables SET load = false WHERE lookup_name IN ('bg', 'sldl', 'sldu', 'tabblock', 'tract', 'vtd');
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
done

${PSQL} "SET maintenance_work_mem = '2GB';
SELECT install_missing_indexes();"
PGOPTIONS="-c maintenance_work_mem=16GB" vacuumdb -U $POSTGRES_USER -a -f -z

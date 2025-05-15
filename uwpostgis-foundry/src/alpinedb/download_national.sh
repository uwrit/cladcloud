#!/bin/bash

usage(){
    echo "Usage: "${0}' [-d domain] [-y year]'
    exit 1
}

# set defaults
[[ -z ${DOMAIN} ]] && DOMAIN="www2.census.gov"
[[ -n ${TIGER_DOMAIN} ]] && DOMAIN=${TIGER_DOMAIN}
[[ -z ${YEAR} ]] && YEAR="2020"
[[ -z ${GISDATA} ]] && GISDATA="/tmp" #"/gisdata"
[[ -z ${OUTDIR} ]] && OUTDIR="${GISDATA}/gisdata/"
[[ -z ${UNZIPTOOL} ]] && UNZIPTOOL=unzip

while getopts "d:s:y:?" arg; do
    case ${arg} in
        d)  DOMAIN=${OPTARG} ;;
        s)  STATES=${OPTARG} ;;
        y)  YEAR=${OPTARG} ;;
        ?)  usage ;;
    esac
done

[[ -z ${BASEPATH} ]] && BASEPATH="${DOMAIN}/geo/tiger/TIGER${YEAR}"
[[ -z ${BASEURL} ]] && BASEURL="http://${BASEPATH}"

mkdir -p ${OUTDIR}

echo '----------------------------------------'
echo "      Adding US national data from "${BASEURL}
echo '----------------------------------------'

cd $GISDATA
wget ${BASEURL}/STATE/tl_${YEAR}_us_state.zip --mirror --reject=html --no-verbose

cd ${BASEPATH}/STATE
for z in tl_*state.zip ;
do
    $UNZIPTOOL -od $OUTDIR $z;
done

cd $GISDATA
wget ${BASEURL}/COUNTY/tl_${YEAR}_us_county.zip --mirror --reject=html --no-verbose

cd ${BASEPATH}/COUNTY
for z in tl_*county.zip ;
do
    $UNZIPTOOL -od $OUTDIR $z;
done

#!/bin/bash

usage(){
    echo "Usage: "${0}' [-d domain] [-s "state[, state...]"] [-y year]'
    exit 1
}

# set defaults
[[ -z ${DOMAIN} ]] && DOMAIN="www2.census.gov"
[[ -n ${TIGER_DOMAIN} ]] && DOMAIN=${TIGER_DOMAIN}
[[ -z ${STATES} ]] && STATES="AL,AK,AZ,AR,CA,CO,CT,DE,FL,GA,HI,ID,IL,IN,IA,KS,KY,LA,ME,MD,MA,MI,MN,MS,MO,MT,NE,NV,NH,NJ,NM,NY,NC,ND,OH,OK,OR,PA,RI,SC,SD,TN,TX,UT,VT,VA,WA,WV,WI,WY"
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

echo '----------------------------------------'
echo ${BASEURL}" + "${STATES}

mkdir -p ${OUTDIR}

get_fips_from_abbr () {
    local fips=0
    case $1 in
        "AL")  fips=01;; "AK")  fips=02;; "AS")  fips=60;; "AZ")  fips=04;; "AR")  fips=05;;
        "CA")  fips=06;; "CO")  fips=08;; "CT")  fips=09;; "DE")  fips=10;; "DC")  fips=11;;
        "FL")  fips=12;; "FM")  fips=64;; "GA")  fips=13;; "GU")  fips=66;; "HI")  fips=15;;
        "ID")  fips=16;; "IL")  fips=17;; "IN")  fips=18;; "IA")  fips=19;; "KS")  fips=20;;
        "KY")  fips=21;; "LA")  fips=22;; "ME")  fips=23;; "MH")  fips=68;; "MD")  fips=24;;
        "MA")  fips=25;; "MI")  fips=26;; "MN")  fips=27;; "MS")  fips=28;; "MO")  fips=29;;
        "MT")  fips=30;; "NE")  fips=31;; "NV")  fips=32;; "NH")  fips=33;; "NJ")  fips=34;;
        "NM")  fips=35;; "NY")  fips=36;; "NC")  fips=37;; "ND")  fips=38;; "MP")  fips=69;;
        "OH")  fips=39;; "OK")  fips=40;; "OR")  fips=41;; "PW")  fips=70;; "PA")  fips=42;;
        "PR")  fips=72;; "RI")  fips=44;; "SC")  fips=45;; "SD")  fips=46;; "TN")  fips=47;;
        "TX")  fips=48;; "UM")  fips=74;; "UT")  fips=49;; "VT")  fips=50;; "VA")  fips=51;;
        "VI")  fips=78;; "WA")  fips=53;; "WV")  fips=54;; "WI")  fips=55;; "WY")  fips=56;;
    esac
    echo $fips
}

get_fips_files () {
    local url=$1
    local fips=$2
    local files=($(wget --no-verbose -O - $url \
        | perl -nle 'print if m{(?=\"tl)(.*?)(?<=>)}g' \
        | perl -nle 'print m{(?=\"tl)(.*?)(?<=>)}g' | sed -e 's/[\"]//g'  | sed -e 's/[>]//g' ))
    local matched=($(echo "${files[*]}" | tr ' ' '\n' | grep "tl_${YEAR}_${fips}"  ))
    echo "${matched[*]}"
}

load_state_data () {
    ABBR=$1
    abbr=$(echo "$ABBR" | perl -ne 'print lc')
    FIPS=$2

    #############
    # Addr
    #############
    cd $GISDATA
    files=($(get_fips_files $BASEURL/ADDR $FIPS))

    for i in "${files[@]}"
    do
        wget $BASEURL/ADDR/$i --no-verbose --mirror
    done

    cd $GISDATA/$BASEPATH/ADDR

    for z in tl_${YEAR}_${FIPS}*_addr.zip ;
    do
        $UNZIPTOOL -o -d $OUTDIR $z;
    done

    #############
    # Place
    #############
    cd $GISDATA
    wget $BASEURL/PLACE/tl_${YEAR}_${FIPS}_place.zip --mirror --reject=html --no-verbose
    cd $GISDATA/$BASEPATH/PLACE

    for z in tl_${YEAR}_${FIPS}*_place.zip ;
    do
        $UNZIPTOOL -o -d $OUTDIR $z;
    done

    #############
    # Cousub
    #############
    cd $GISDATA
    wget $BASEURL/COUSUB/tl_${YEAR}_${FIPS}_cousub.zip --mirror --reject=html --no-verbose
    cd $GISDATA/$BASEPATH/COUSUB

    for z in tl_${YEAR}_${FIPS}*_cousub.zip ;
    do
        $UNZIPTOOL -o -d $OUTDIR $z;
    done

    #############
    # Tract
    #############
    cd $GISDATA
    wget $BASEURL/TRACT/tl_${YEAR}_${FIPS}_tract.zip --mirror --reject=html --no-verbose
    cd $GISDATA/$BASEPATH/TRACT

    for z in tl_${YEAR}_${FIPS}*_tract.zip ;
    do
        $UNZIPTOOL -o -d $OUTDIR $z;
    done

    #############
    # Faces
    #############
    cd $GISDATA
    files=($(get_fips_files $BASEURL/FACES $FIPS))

    for i in "${files[@]}"
    do
        wget $BASEURL/FACES/$i --no-verbose --mirror
    done

    cd $GISDATA/$BASEPATH/FACES/

    for z in tl_${YEAR}_${FIPS}*_faces.zip ;
    do
        $UNZIPTOOL -o -d $OUTDIR $z;
    done

    #############
    # FeatNames
    #############
    cd $GISDATA
    files=($(get_fips_files $BASEURL/FEATNAMES $FIPS))

    for i in "${files[@]}"
    do
        wget $BASEURL/FEATNAMES/$i --no-verbose --mirror
    done

    cd $GISDATA/$BASEPATH/FEATNAMES/

    for z in tl_${YEAR}_${FIPS}*_featnames.zip ;
    do
        $UNZIPTOOL -o -d $OUTDIR $z;
    done
    cd $OUTDIR;

    #############
    # Edges
    #############
    cd $GISDATA
    files=($(get_fips_files $BASEURL/EDGES $FIPS))

    for i in "${files[@]}"
    do
        wget $BASEURL/EDGES/$i --no-verbose --mirror
    done

    cd $GISDATA/$BASEPATH/EDGES

    for z in tl_${YEAR}_${FIPS}*_edges.zip ;
    do
        $UNZIPTOOL -o -d $OUTDIR $z;
    done
}

# For each selected state
IFS=',' read -ra GEO_STATES <<< "${STATES^^}"
for ABBR in "${GEO_STATES[@]}";
do
    FIPS=$(get_fips_from_abbr $ABBR)
    if [ $FIPS -eq 0 ]; then
        echo "Error: '$ABBR' is not a recognized US state abbreviation"
    else
        echo '----------------------------------------'
        echo "      Loading state data for: '$ABBR $FIPS'"
        echo '----------------------------------------'
        load_state_data $ABBR $FIPS
    fi
done

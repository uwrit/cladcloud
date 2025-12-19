#!/usr/bin/env bash

# uses the "run.sh" scripts for each container

# first build degauss and test
echo "Building image..."
docker build \
  --platform linux/amd64 \
  -t degauss-foundry \
  -f Dockerfile \
  degauss-foundry


echo "Scanning image for CVEs..."
./scripts/scan_image.sh degauss-foundry

# TODO: ideally here we run the container to test it
# NOTE: this would require preparing some data and for `postgis`
# filtering it to the corresponding state
echo "Running docker container..."
# docker run \
#   --rm \
#   --name degauss-foundry-container \
#   --platform linux/amd64 \
#   -v "${PWD}/data:/opt/palantir/sidecars/shared-volumes/shared" \
#   degauss-foundry
#
# TODO: then run some sort of analytical check to see if the speed 
# and accuracy were within expectations
# uv run XXX
#

echo "Removing container..."
docker image rm degauss-foundry

echo "Finished degauss."

echo "Starting PostGIS processing..."

STATES=("AL,AK,AZ,AR,CA,CO,CT,DE,FL,GA,HI,ID,IL,IN,IA,KS,KY,LA,ME,MD,MA,MI,MN,MS,MO,MT,NE,NV,NH,NJ,NM,NY,NC,ND,OH,OK,OR,PA,RI,SC,SD,TN,TX,UT,VT,VA,WA,WV,WI,WY")

for state in "${STATES[@]}"; do
  echo "Working on $state..."

  echo "Building state image..."
    docker build \
    --platform linux/amd64 \
    --build-arg DOMAIN=clad-github-builder.rit.uw.edu \
    --build-arg STATE="${state}"\
    --build-arg YEAR=2020 \
    --tag postgis-state \
    -f Dockerfile \
    uwpostgis-foundry

    echo "Scanning image for CVEs..."
    ./scripts/scan_image.sh postgis-state

    echo "Removing image..."
    docker image rm postgis-state


    # TODO: same thing here as above, 
    # - run container to prove it works
    # - examine metrics to prove w/in expectations

    echo "Moving on..."

done


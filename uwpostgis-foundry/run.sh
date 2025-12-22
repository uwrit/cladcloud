#! /usr/bin/env bash

set -e

mkdir -p data
# copy data file
cp ../data/florida.csv data/example.csv
cp ../data/flag_file data/start_flag
# remove old output
rm -f data/example_output.csv


# examples of two valid DOMAINs
# --build-arg DOMAIN=www2.census.gov \
# --build-arg DOMAIN=clad-github-builder.rit.uw.edu \

echo "Building image..."
docker build \
  --progress=plain \
  --platform linux/amd64 \
  --build-arg DOMAIN=clad-github-builder.rit.uw.edu \
  --build-arg STATE=FL \
  --build-arg YEAR=2020 \
  --tag postgis-fl \
  -f Dockerfile \
  . 

echo "Running trivy scan..."
trivy image postgis-fl

echo "Running docker container..."
docker run \
  --rm \
  --name postgis-fl-container \
  --platform linux/amd64 \
  -v "${PWD}/data:/opt/palantir/sidecars/shared-volumes/shared" \
  postgis-fl


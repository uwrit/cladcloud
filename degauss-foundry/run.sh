#! /usr/bin/env bash

set -e

mkdir -p data
# copy data file
cp ../data/florida.csv data/example.csv
cp ../data/flag_file data/start_flag
# remove old output
rm -f data/example_output.csv

echo "Building image..."
docker build \
  --platform=linux/amd64 \
  -t degauss-foundry . 

echo "Running trivy scan..."
trivy image degauss-foundry

echo "Running docker container..."
docker run \
  --rm \
  --name degauss-foundry-container \
  -v "${PWD}/data:/opt/palantir/sidecars/shared-volumes/shared" \
  degauss-foundry

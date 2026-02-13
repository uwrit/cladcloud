#!/usr/bin/env bash

set -e

mkdir -p data

# NOTE: container makes "done_flag"
cp flag_file data/start_flag
cp flag_file data/close_flag

# build inside degauss folder context
docker build \
    -t postgis-test \
    --platform=linux/amd64 \
    -f Dockerfile \
    uwpostgis

docker run --rm \
    --platform=linux/amd64 \
    -v "${PWD}"/data:/opt/palantir/sidecars/shared-volumes/shared \
    --name postgis-test-container \
    postgis-test



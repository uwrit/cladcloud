#!/usr/bin/env bash

set -euo pipefail

if [ -z "$1" ]; then
    echo "Error: No image supplied."
    exit 1
fi

IMAGE=$1

echo "Running trivy..."
trivy image \
    --severity HIGH,CRITICAL \
    --exit-code 1 \
    --no-progress \
    "${IMAGE}"


echo "Running Docker Scout..."
docker scout cves \
    --only-severity critical,high \
    --exit-code \
    "${IMAGE}"


echo "Docker Scout recommendations..."
docker scout recommendations "${IMAGE}"

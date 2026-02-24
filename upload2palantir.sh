#!/bin/bash
REPOSITORY=ri.artifacts.main.repository.768bba05-8acc-46e4-90ad-ee3a0db57a2c
TOKEN=$1
echo Begin $(date -Is)
docker login -u "$REPOSITORY" -p "$TOKEN" genoa-container-registry.washington.palantircloud.com
docker image list --format "{{.Repository}}:{{.Tag}}" | grep palantircloud | sort | xargs -n1 docker push
echo End $(date -Is)

#!/bin/bash
REPOSITORY=ri.artifacts.main.repository.73699721-696b-4909-ad69-e64ef484b180
echo Begin $(date -Is)
echo $1 | docker login -u "$REPOSITORY" --password-stdin genoa-container-registry.washington.palantircloud.com
docker image list --format "{{.Repository}}:{{.Tag}}" | grep palantircloud | sort | xargs -n1 docker push --platform=linux/amd64
echo End $(date -Is)

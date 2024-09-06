# Turning the R Degauss Geocoder implementation into Foundry Ready

Pulling from here:  https://github.com/degauss-org/geocoder/tree/master


Core Steps:

- Transitioning to Alpine Linux
- Implementing Foundry Container Setup guidance.


## Foundry Guidance

https://gitlab.iths.org/bmi-consults/clad-geocoding/-/blob/main/Foundry_Container_SOP.md?ref_type=heads


## Build Container

cd to same directory as Dockerfile.

```

docker buildx build —platform linux/amd64 -t degauss-foundry .

```

## Test Container Locally for Proper Entrypoint behavior.

```
docker run --shm-size=2g --platform linux/amd64 degauss-foundry

export CONTAINER_ID=$(docker ps -q)

docker cp /Users/jtl/Desktop/uma_fips/degauss_foundry/infile.csv $CONTAINER_ID:/opt/palantir/sidecars/shared-volumes/shared/infile.csv

touch flag_file

docker cp flag_file $CONTAINER_ID:/opt/palantir/sidecars/shared-volumes/shared/start_flag

docker cp $CONTAINER_ID:/opt/palantir/sidecars/shared-volumes/shared/outfile_geocoder_3.3.0.csv /Users/jtl/Desktop/uma_fips/degauss_foundry/outfile.csv

docker cp flag_file $CONTAINER_ID:/opt/palantir/sidecars/shared-volumes/shared/close_flag

```


# uwpostgis-foundry
This is a single purpose container for supporting just the geocoding functions of postgis with the slimmest possible approach. Tabblock TIGER file import not needed. 

This is customized to work as a sidecar within the context of




### SQL Query Definition

You pass the geocode() function a string and you get back a set of columns. 

```sql

    SELECT 
                      g.rating
                    , ST_AsText(ST_SnapToGrid(g.geomout,0.00001)) As wktlonlat
                    , (addy).address As stno
                    , (addy).streetname As street
                    , (addy).streettypeabbrev As styp
                    , (addy).location As city
                    , (addy).stateabbrev As st
                    , (addy).zip
                    FROM geocode('Address string goes here') As g;


```

An adjustment to return json would looke like this

```

select row_to_json(geo) geocoded
from (
    SELECT 
                      g.rating
                    , ST_AsText(ST_SnapToGrid(g.geomout,0.00001)) As wktlonlat
                    , (addy).address As stno
                    , (addy).streetname As street
                    , (addy).streettypeabbrev As styp
                    , (addy).location As city
                    , (addy).stateabbrev As st
                    , (addy).zip
                    FROM geocode('Address string goes here') as g) geo;

```

For what's possible here see:

- https://postgis.net/docs/Geocode.html  

- https://postgis.net/docs/using_postgis_dbmanagement.html  


### Foundry Implementation Notes
10/3 Next Steps:

- add python and standard Foundry entrypoint.py approach into Dockerfile - DONE 10/4
- add process_csv.py for actually running the postgres query against the CSV and saving the results - DONE 10/4

1. checkin to main
2. auto rebuild postgis - default WA
3. auto rebuild degauss - default ALL US
4. ad-hoc rebuild - derive new folders for each state to build from - or use injectable ENV variables to select which state to build for
5. shell script for uploading the batch of containers all with a single token




### Build operation

The generic build needs 4gb to pre-process the downloaded files. The default builds an pre-initialized image for the state of Washington tha amounts to about 5gb.

Change the build-arg in the command line file to choose your state. Other settings can remain the same unless you want to inject a different POSTGRES_PASSWORD at build time too. We'll need to think about injecting that new password into the process_csv.py as well. 

```
cd postgis-docker-alpine-db

docker buildx build --shm-size 4g --no-cache -t uwpostgis-foundry-wa .

docker buildx build --shm-size 4g --no-cache -t uwpostgis-foundry-tx .


docker buildx build --shm-size 4g -t uwpostgis-foundry-ak --build-arg GEOCODER_STATES=AK .


```

The build process on a local computer takes 15-20 minutes for a single container:  download OS and OS packages, download the tiger files, and then pre-initialize the database.

- alpine OS layers: 10mb
- Tiger download for WA layers: 2.4 GB
- postgres initialization for just WA:  2.8 GB



### Testing


```
touch flag_file

docker run --platform linux/amd64 uwpostgis-foundry-ak



export CONTAINER_ID=e71ee32802b5372abb64182cf8436c89a4c4533c195978a270205d00d2705119
docker cp /Users/jtl/Documents/ak_infile.csv $CONTAINER_ID:/opt/palantir/sidecars/shared-volumes/shared/infile.csv
docker cp flag_file $CONTAINER_ID:/opt/palantir/sidecars/shared-volumes/shared/start_flag

docker cp $CONTAINER_ID:/opt/palantir/sidecars/shared-volumes/shared/outfile.csv /Users/jtl/Documents/outfile_ak.csv

docker cp flag_file $CONTAINER_ID:/opt/palantir/sidecars/shared-volumes/shared/close_flag

```


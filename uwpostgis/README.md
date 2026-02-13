# postgis
This is a single purpose container for supporting just the geocoding functions of postgis with the slimmest possible approach. Tabblock TIGER file import not needed.

This is customized to work as a sidecar within the context of the Palantir foundry cloud environment


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

  - [x] add python and standard Foundry geocode.py approach into Dockerfile - DONE 10/4
  - [x] add process_csv.py for actually running the postgres query against the CSV and saving the results - DONE 10/4

  - [x] checkin to main
  - [x] auto rebuild postgis - default WA
  - [x] auto rebuild degauss - default ALL US
  - [x] ad-hoc rebuild - derive new folders for each state to build from - or use injectable ENV variables to select which state to build for
  - [x] shell script for uploading the batch of containers all with a single token


### Build operation

The generic build needs 4gb to pre-process the downloaded files. The default builds an pre-initialized image for the state of Washington tha amounts to about 5gb.

Change the build-arg in the command line file to choose your state. Other settings can remain the same unless you want to inject a different POSTGRES_PASSWORD at build time too. We'll need to think about injecting that new password into the process_csv.py as well.

```bash
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


```bash
touch flag_file

docker run --platform linux/amd64 uwpostgis-foundry-ak

export CONTAINER_ID=e71ee32802b5372abb64182cf8436c89a4c4533c195978a270205d00d2705119
docker cp /Users/jtl/Documents/ak_infile.csv $CONTAINER_ID:/opt/palantir/sidecars/shared-volumes/shared/infile.csv
docker cp flag_file $CONTAINER_ID:/opt/palantir/sidecars/shared-volumes/shared/start_flag

docker cp $CONTAINER_ID:/opt/palantir/sidecars/shared-volumes/shared/outfile.csv /Users/jtl/Documents/outfile_ak.csv

docker cp flag_file $CONTAINER_ID:/opt/palantir/sidecars/shared-volumes/shared/close_flag
```



## Territories Shapefile availability
 Territory | EDGES | ADDR | FACES | PLACE| COUSUB |
| -- | -- | -- | -- | -- | --|
| American Samoa (AS) - 60 | Y | 2020: No, 2024: No | Y | Y | Y |
| Guam (GU) 66 | Y | 2020: No, 2024: Yes | Y | Y | Y |
| Puerto Rico (PR) - 72| Y | Y | Y | Y | Y |
| Virgin Islands (VI) - 78| Y | 2020: No, 2024: Yes| Y | Y | Y |

### American Samoa

```
#15 4.346 ----------------------------------------
#15 4.346       Loading state data for: 'AS 60'
#15 4.346 ----------------------------------------
#15 4.474 2025-02-13 00:26:41 URL:https://www2.census.gov/geo/tiger/TIGER2020/ADDR/ [748577] -> "-" [1]
#15 4.522 ./state_download_layer.sh: line 88: cd: /gisdata/www2.census.gov/geo/tiger/TIGER2020/ADDR: No such file or directory
#15 4.525 unzip:  cannot find or open tl_2020_60*_addr.zip, tl_2020_60*_addr.zip.zip or tl_2020_60*_addr.zip.ZIP.
#15 4.525
#15 4.525 No zipfiles found.
#15 4.689 2025-02-13 00:26:41 URL:https://www2.census.gov/geo/tiger/TIGER2020/PLACE/tl_2020_60_place.zip [80539] -> "www2.census.gov/geo/tiger/TIGER2020/PLACE/tl_2020_60_place.zip" [1]
#15 4.689 FINISHED --2025-02-13 00:26:41--
#15 4.689 Total wall clock time: 0.2s
#15 4.689 Downloaded: 1 files, 79K in 0.002s (32.8 MB/s)
#15 4.695 Archive:  tl_2020_60_place.zip
#15 4.696  extracting: /gisdata/temp/tl_2020_60_place.cpg
#15 4.697   inflating: /gisdata/temp/tl_2020_60_place.dbf
#15 4.698   inflating: /gisdata/temp/tl_2020_60_place.prj
#15 4.698   inflating: /gisdata/temp/tl_2020_60_place.shp
#15 4.702   inflating: /gisdata/temp/tl_2020_60_place.shp.ea.iso.xml
#15 4.704   inflating: /gisdata/temp/tl_2020_60_place.shp.iso.xml
#15 4.705   inflating: /gisdata/temp/tl_2020_60_place.shx
#15 4.878 2025-02-13 00:26:41 URL:https://www2.census.gov/geo/tiger/TIGER2020/COUSUB/tl_2020_60_cousub.zip [31892/31892] -> "www2.census.gov/geo/tiger/TIGER2020/COUSUB/tl_2020_60_cousub.zip" [1]
#15 4.878 FINISHED --2025-02-13 00:26:41--
#15 4.878 Total wall clock time: 0.2s
#15 4.878 Downloaded: 1 files, 31K in 0s (115 MB/s)
#15 4.884 Archive:  tl_2020_60_cousub.zip
#15 4.885  extracting: /gisdata/temp/tl_2020_60_cousub.cpg
#15 4.885   inflating: /gisdata/temp/tl_2020_60_cousub.dbf
#15 4.886   inflating: /gisdata/temp/tl_2020_60_cousub.prj
#15 4.886   inflating: /gisdata/temp/tl_2020_60_cousub.shp
#15 4.888   inflating: /gisdata/temp/tl_2020_60_cousub.shp.ea.iso.xml
#15 4.890   inflating: /gisdata/temp/tl_2020_60_cousub.shp.iso.xml
#15 4.891   inflating: /gisdata/temp/tl_2020_60_cousub.shx
#15 5.023 2025-02-13 00:26:41 URL:https://www2.census.gov/geo/tiger/TIGER2020/TRACT/tl_2020_60_tract.zip [39488/39488] -> "www2.census.gov/geo/tiger/TIGER2020/TRACT/tl_2020_60_tract.zip" [1]
#15 5.023 FINISHED --2025-02-13 00:26:41--
#15 5.023 Total wall clock time: 0.1s
#15 5.023 Downloaded: 1 files, 39K in 0s (92.0 MB/s)
#15 5.030 Archive:  tl_2020_60_tract.zip
#15 5.030  extracting: /gisdata/temp/tl_2020_60_tract.cpg
#15 5.031   inflating: /gisdata/temp/tl_2020_60_tract.dbf
#15 5.031   inflating: /gisdata/temp/tl_2020_60_tract.prj
#15 5.032   inflating: /gisdata/temp/tl_2020_60_tract.shp
#15 5.034   inflating: /gisdata/temp/tl_2020_60_tract.shp.ea.iso.xml
#15 5.034   inflating: /gisdata/temp/tl_2020_60_tract.shp.iso.xml
#15 5.035   inflating: /gisdata/temp/tl_2020_60_tract.shx
#15 5.333 2025-02-13 00:26:41 URL:https://www2.census.gov/geo/tiger/TIGER2020/FACES/ [758010] -> "-" [1]
#15 6.196 2025-02-13 00:26:42 URL:https://www2.census.gov/geo/tiger/TIGER2020/FACES/tl_2020_60010_faces.zip [534845] -> "www2.census.gov/geo/tiger/TIGER2020/FACES/tl_2020_60010_faces.zip" [1]
#15 6.196 FINISHED --2025-02-13 00:26:42--
#15 6.196 Total wall clock time: 0.8s
#15 6.196 Downloaded: 1 files, 522K in 0.5s (998 KB/s)
#15 6.555 2025-02-13 00:26:43 URL:https://www2.census.gov/geo/tiger/TIGER2020/FACES/tl_2020_60020_faces.zip [155906] -> "www2.census.gov/geo/tiger/TIGER2020/FACES/tl_2020_60020_faces.zip" [1]
#15 6.555 FINISHED --2025-02-13 00:26:43--
#15 6.555 Total wall clock time: 0.4s
#15 6.555 Downloaded: 1 files, 152K in 0.1s (1015 KB/s)
#15 7.087 2025-02-13 00:26:43 URL:https://www2.census.gov/geo/tiger/TIGER2020/FACES/tl_2020_60030_faces.zip [16986/16986] -> "www2.census.gov/geo/tiger/TIGER2020/FACES/tl_2020_60030_faces.zip" [1]
#15 7.087 FINISHED --2025-02-13 00:26:43--
#15 7.087 Total wall clock time: 0.5s
#15 7.087 Downloaded: 1 files, 17K in 0.001s (27.3 MB/s)
#15 7.397 2025-02-13 00:26:44 URL:https://www2.census.gov/geo/tiger/TIGER2020/FACES/tl_2020_60040_faces.zip [17421/17421] -> "www2.census.gov/geo/tiger/TIGER2020/FACES/tl_2020_60040_faces.zip" [1]
#15 7.397 FINISHED --2025-02-13 00:26:44--
#15 7.397 Total wall clock time: 0.3s
#15 7.397 Downloaded: 1 files, 17K in 0s (79.6 MB/s)
#15 8.211 2025-02-13 00:26:44 URL:https://www2.census.gov/geo/tiger/TIGER2020/FACES/tl_2020_60050_faces.zip [548933] -> "www2.census.gov/geo/tiger/TIGER2020/FACES/tl_2020_60050_faces.zip" [1]
#15 8.211 FINISHED --2025-02-13 00:26:44--
#15 8.211 Total wall clock time: 0.8s
#15 8.211 Downloaded: 1 files, 536K in 0.6s (848 KB/s)
#15 8.219 Archive:  tl_2020_60010_faces.zip
#15 8.219  extracting: /gisdata/temp/tl_2020_60010_faces.cpg
#15 8.221   inflating: /gisdata/temp/tl_2020_60010_faces.dbf
#15 8.225   inflating: /gisdata/temp/tl_2020_60010_faces.prj
#15 8.225   inflating: /gisdata/temp/tl_2020_60010_faces.shp
#15 8.238   inflating: /gisdata/temp/tl_2020_60010_faces.shp.ea.iso.xml
#15 8.239   inflating: /gisdata/temp/tl_2020_60010_faces.shp.iso.xml
#15 8.240   inflating: /gisdata/temp/tl_2020_60010_faces.shx
#15 8.245 Archive:  tl_2020_60020_faces.zip
#15 8.245  extracting: /gisdata/temp/tl_2020_60020_faces.cpg
#15 8.246   inflating: /gisdata/temp/tl_2020_60020_faces.dbf
#15 8.247   inflating: /gisdata/temp/tl_2020_60020_faces.prj
#15 8.248   inflating: /gisdata/temp/tl_2020_60020_faces.shp
#15 8.253   inflating: /gisdata/temp/tl_2020_60020_faces.shp.ea.iso.xml
#15 8.255   inflating: /gisdata/temp/tl_2020_60020_faces.shp.iso.xml
#15 8.255   inflating: /gisdata/temp/tl_2020_60020_faces.shx
#15 8.258 Archive:  tl_2020_60030_faces.zip
#15 8.258  extracting: /gisdata/temp/tl_2020_60030_faces.cpg
#15 8.259   inflating: /gisdata/temp/tl_2020_60030_faces.dbf
#15 8.259   inflating: /gisdata/temp/tl_2020_60030_faces.prj
#15 8.259   inflating: /gisdata/temp/tl_2020_60030_faces.shp
#15 8.260   inflating: /gisdata/temp/tl_2020_60030_faces.shp.ea.iso.xml
#15 8.262   inflating: /gisdata/temp/tl_2020_60030_faces.shp.iso.xml
#15 8.263   inflating: /gisdata/temp/tl_2020_60030_faces.shx
#15 8.266 Archive:  tl_2020_60040_faces.zip
#15 8.266  extracting: /gisdata/temp/tl_2020_60040_faces.cpg
#15 8.266   inflating: /gisdata/temp/tl_2020_60040_faces.dbf
#15 8.266   inflating: /gisdata/temp/tl_2020_60040_faces.prj
#15 8.266   inflating: /gisdata/temp/tl_2020_60040_faces.shp
#15 8.266   inflating: /gisdata/temp/tl_2020_60040_faces.shp.ea.iso.xml
#15 8.267   inflating: /gisdata/temp/tl_2020_60040_faces.shp.iso.xml
#15 8.268   inflating: /gisdata/temp/tl_2020_60040_faces.shx
#15 8.272 Archive:  tl_2020_60050_faces.zip
#15 8.272  extracting: /gisdata/temp/tl_2020_60050_faces.cpg
#15 8.273   inflating: /gisdata/temp/tl_2020_60050_faces.dbf
#15 8.276   inflating: /gisdata/temp/tl_2020_60050_faces.prj
#15 8.276   inflating: /gisdata/temp/tl_2020_60050_faces.shp
#15 8.288   inflating: /gisdata/temp/tl_2020_60050_faces.shp.ea.iso.xml
#15 8.289   inflating: /gisdata/temp/tl_2020_60050_faces.shp.iso.xml
#15 8.289   inflating: /gisdata/temp/tl_2020_60050_faces.shx
#15 8.459 2025-02-13 00:26:45 URL:https://www2.census.gov/geo/tiger/TIGER2020/FEATNAMES/ [783886] -> "-" [1]
#15 8.788 2025-02-13 00:26:45 URL:https://www2.census.gov/geo/tiger/TIGER2020/FEATNAMES/tl_2020_60010_featnames.zip [44517] -> "www2.census.gov/geo/tiger/TIGER2020/FEATNAMES/tl_2020_60010_featnames.zip" [1]
#15 8.788 FINISHED --2025-02-13 00:26:45--
#15 8.788 Total wall clock time: 0.3s
#15 8.788 Downloaded: 1 files, 43K in 0.001s (76.8 MB/s)
#15 8.981 2025-02-13 00:26:45 URL:https://www2.census.gov/geo/tiger/TIGER2020/FEATNAMES/tl_2020_60020_featnames.zip [14168/14168] -> "www2.census.gov/geo/tiger/TIGER2020/FEATNAMES/tl_2020_60020_featnames.zip" [1]
#15 8.981 FINISHED --2025-02-13 00:26:45--
#15 8.981 Total wall clock time: 0.2s
#15 8.981 Downloaded: 1 files, 14K in 0s (146 MB/s)
#15 9.207 2025-02-13 00:26:45 URL:https://www2.census.gov/geo/tiger/TIGER2020/FEATNAMES/tl_2020_60030_featnames.zip [9563/9563] -> "www2.census.gov/geo/tiger/TIGER2020/FEATNAMES/tl_2020_60030_featnames.zip" [1]
#15 9.207 FINISHED --2025-02-13 00:26:45--
#15 9.207 Total wall clock time: 0.2s
#15 9.207 Downloaded: 1 files, 9.3K in 0s (343 MB/s)
#15 9.394 2025-02-13 00:26:46 URL:https://www2.census.gov/geo/tiger/TIGER2020/FEATNAMES/tl_2020_60040_featnames.zip [9574/9574] -> "www2.census.gov/geo/tiger/TIGER2020/FEATNAMES/tl_2020_60040_featnames.zip" [1]
#15 9.394 FINISHED --2025-02-13 00:26:46--
#15 9.394 Total wall clock time: 0.2s
#15 9.394 Downloaded: 1 files, 9.3K in 0s (251 MB/s)
#15 9.601 2025-02-13 00:26:46 URL:https://www2.census.gov/geo/tiger/TIGER2020/FEATNAMES/tl_2020_60050_featnames.zip [61113] -> "www2.census.gov/geo/tiger/TIGER2020/FEATNAMES/tl_2020_60050_featnames.zip" [1]
#15 9.601 FINISHED --2025-02-13 00:26:46--
#15 9.601 Total wall clock time: 0.2s
#15 9.601 Downloaded: 1 files, 60K in 0.001s (55.9 MB/s)
#15 9.608 Archive:  tl_2020_60010_featnames.zip
#15 9.608  extracting: /gisdata/temp/tl_2020_60010_featnames.cpg
#15 9.608   inflating: /gisdata/temp/tl_2020_60010_featnames.dbf
#15 9.618   inflating: /gisdata/temp/tl_2020_60010_featnames.shp.ea.iso.xml
#15 9.619   inflating: /gisdata/temp/tl_2020_60010_featnames.shp.iso.xml
#15 9.623 Archive:  tl_2020_60020_featnames.zip
#15 9.623  extracting: /gisdata/temp/tl_2020_60020_featnames.cpg
#15 9.623   inflating: /gisdata/temp/tl_2020_60020_featnames.dbf
#15 9.625   inflating: /gisdata/temp/tl_2020_60020_featnames.shp.ea.iso.xml
#15 9.625   inflating: /gisdata/temp/tl_2020_60020_featnames.shp.iso.xml
#15 9.630 Archive:  tl_2020_60030_featnames.zip
#15 9.631  extracting: /gisdata/temp/tl_2020_60030_featnames.cpg
#15 9.631   inflating: /gisdata/temp/tl_2020_60030_featnames.dbf
#15 9.632   inflating: /gisdata/temp/tl_2020_60030_featnames.shp.ea.iso.xml
#15 9.633   inflating: /gisdata/temp/tl_2020_60030_featnames.shp.iso.xml
#15 9.637 Archive:  tl_2020_60040_featnames.zip
#15 9.638  extracting: /gisdata/temp/tl_2020_60040_featnames.cpg
#15 9.638   inflating: /gisdata/temp/tl_2020_60040_featnames.dbf
#15 9.639   inflating: /gisdata/temp/tl_2020_60040_featnames.shp.ea.iso.xml
#15 9.639   inflating: /gisdata/temp/tl_2020_60040_featnames.shp.iso.xml
#15 9.645 Archive:  tl_2020_60050_featnames.zip
#15 9.645  extracting: /gisdata/temp/tl_2020_60050_featnames.cpg
#15 9.646   inflating: /gisdata/temp/tl_2020_60050_featnames.dbf
#15 9.659   inflating: /gisdata/temp/tl_2020_60050_featnames.shp.ea.iso.xml
#15 9.660   inflating: /gisdata/temp/tl_2020_60050_featnames.shp.iso.xml
#15 9.793 2025-02-13 00:26:46 URL:https://www2.census.gov/geo/tiger/TIGER2020/EDGES/ [758010] -> "-" [1]
#15 10.61 2025-02-13 00:26:47 URL:https://www2.census.gov/geo/tiger/TIGER2020/EDGES/tl_2020_60010_edges.zip [538456] -> "www2.census.gov/geo/tiger/TIGER2020/EDGES/tl_2020_60010_edges.zip" [1]
#15 10.61 FINISHED --2025-02-13 00:26:47--
#15 10.61 Total wall clock time: 0.8s
#15 10.61 Downloaded: 1 files, 526K in 0.4s (1.26 MB/s)
#15 10.93 2025-02-13 00:26:47 URL:https://www2.census.gov/geo/tiger/TIGER2020/EDGES/tl_2020_60020_edges.zip [145137] -> "www2.census.gov/geo/tiger/TIGER2020/EDGES/tl_2020_60020_edges.zip" [1]
#15 10.93 FINISHED --2025-02-13 00:26:47--
#15 10.93 Total wall clock time: 0.3s
#15 10.93 Downloaded: 1 files, 142K in 0.1s (1.06 MB/s)
#15 11.12 2025-02-13 00:26:47 URL:https://www2.census.gov/geo/tiger/TIGER2020/EDGES/tl_2020_60030_edges.zip [15825/15825] -> "www2.census.gov/geo/tiger/TIGER2020/EDGES/tl_2020_60030_edges.zip" [1]
#15 11.12 FINISHED --2025-02-13 00:26:47--
#15 11.12 Total wall clock time: 0.2s
#15 11.12 Downloaded: 1 files, 15K in 0.001s (30.1 MB/s)
#15 11.28 2025-02-13 00:26:47 URL:https://www2.census.gov/geo/tiger/TIGER2020/EDGES/tl_2020_60040_edges.zip [16735/16735] -> "www2.census.gov/geo/tiger/TIGER2020/EDGES/tl_2020_60040_edges.zip" [1]
#15 11.28 FINISHED --2025-02-13 00:26:47--
#15 11.28 Total wall clock time: 0.1s
#15 11.28 Downloaded: 1 files, 16K in 0.001s (30.1 MB/s)
#15 12.17 2025-02-13 00:26:48 URL:https://www2.census.gov/geo/tiger/TIGER2020/EDGES/tl_2020_60050_edges.zip [625480] -> "www2.census.gov/geo/tiger/TIGER2020/EDGES/tl_2020_60050_edges.zip" [1]
#15 12.17 FINISHED --2025-02-13 00:26:48--
#15 12.17 Total wall clock time: 0.9s
#15 12.17 Downloaded: 1 files, 611K in 0.7s (869 KB/s)
#15 12.18 Archive:  tl_2020_60010_edges.zip
#15 12.18  extracting: /gisdata/temp/tl_2020_60010_edges.cpg
#15 12.18   inflating: /gisdata/temp/tl_2020_60010_edges.dbf
#15 12.20   inflating: /gisdata/temp/tl_2020_60010_edges.prj
#15 12.20   inflating: /gisdata/temp/tl_2020_60010_edges.shp
#15 12.21   inflating: /gisdata/temp/tl_2020_60010_edges.shp.ea.iso.xml
#15 12.21   inflating: /gisdata/temp/tl_2020_60010_edges.shp.iso.xml
#15 12.21   inflating: /gisdata/temp/tl_2020_60010_edges.shx
#15 12.21 Archive:  tl_2020_60020_edges.zip
#15 12.21  extracting: /gisdata/temp/tl_2020_60020_edges.cpg
#15 12.21   inflating: /gisdata/temp/tl_2020_60020_edges.dbf
#15 12.22   inflating: /gisdata/temp/tl_2020_60020_edges.prj
#15 12.22   inflating: /gisdata/temp/tl_2020_60020_edges.shp
#15 12.22   inflating: /gisdata/temp/tl_2020_60020_edges.shp.ea.iso.xml
#15 12.22   inflating: /gisdata/temp/tl_2020_60020_edges.shp.iso.xml
#15 12.22   inflating: /gisdata/temp/tl_2020_60020_edges.shx
#15 12.23 Archive:  tl_2020_60030_edges.zip
#15 12.23  extracting: /gisdata/temp/tl_2020_60030_edges.cpg
#15 12.23   inflating: /gisdata/temp/tl_2020_60030_edges.dbf
#15 12.23   inflating: /gisdata/temp/tl_2020_60030_edges.prj
#15 12.23   inflating: /gisdata/temp/tl_2020_60030_edges.shp
#15 12.23   inflating: /gisdata/temp/tl_2020_60030_edges.shp.ea.iso.xml
#15 12.23   inflating: /gisdata/temp/tl_2020_60030_edges.shp.iso.xml
#15 12.23   inflating: /gisdata/temp/tl_2020_60030_edges.shx
#15 12.23 Archive:  tl_2020_60040_edges.zip
#15 12.23  extracting: /gisdata/temp/tl_2020_60040_edges.cpg
#15 12.23   inflating: /gisdata/temp/tl_2020_60040_edges.dbf
#15 12.23   inflating: /gisdata/temp/tl_2020_60040_edges.prj
#15 12.23   inflating: /gisdata/temp/tl_2020_60040_edges.shp
#15 12.23   inflating: /gisdata/temp/tl_2020_60040_edges.shp.ea.iso.xml
#15 12.24   inflating: /gisdata/temp/tl_2020_60040_edges.shp.iso.xml
#15 12.24   inflating: /gisdata/temp/tl_2020_60040_edges.shx
#15 12.24 Archive:  tl_2020_60050_edges.zip
#15 12.24  extracting: /gisdata/temp/tl_2020_60050_edges.cpg
#15 12.24   inflating: /gisdata/temp/tl_2020_60050_edges.dbf
#15 12.25   inflating: /gisdata/temp/tl_2020_60050_edges.prj
#15 12.25   inflating: /gisdata/temp/tl_2020_60050_edges.shp
#15 12.26   inflating: /gisdata/temp/tl_2020_60050_edges.shp.ea.iso.xml
#15 12.26   inflating: /gisdata/temp/tl_2020_60050_edges.shp.iso.xml
#15 12.26   inflating: /gisdata/temp/tl_2020_60050_edges.shx
#15 DONE 12.3s

#16 [buildtime_init_builder 9/9] RUN docker-entrypoint.sh postgres
#16 0.459 The files belonging to this database system will be owned by user "postgres".
#16 0.459 This user must also own the server process.
#16 0.459
#16 0.459 The database cluster will be initialized with locale "en_US.utf8".
#16 0.459 The default database encoding has accordingly been set to "UTF8".
#16 0.459 The default text search configuration will be set to "english".
#16 0.459
#16 0.459 Data page checksums are disabled.
#16 0.459
#16 0.461 fixing permissions on existing directory /pgdata ... ok
#16 0.461 creating subdirectories ... ok
#16 0.464 selecting dynamic shared memory implementation ... posix
#16 0.464 selecting default max_connections ... 100
#16 0.491 selecting default shared_buffers ... 128MB
#16 0.529 selecting default time zone ... UTC
#16 0.588 creating configuration files ... ok
#16 0.590 running bootstrap script ... ok
#16 0.835 performing post-bootstrap initialization ... sh: locale: not found
#16 1.089 2025-02-13 00:26:50.024 UTC [36] WARNING:  no usable system locales were found
#16 1.666 ok
#16 1.666 syncing data to disk ... ok
#16 3.026
#16 3.026
#16 3.026 Success. You can now start the database server using:
#16 3.026
#16 3.026     pg_ctl -D /pgdata -l logfile start
#16 3.026
#16 3.026 initdb: warning: enabling "trust" authentication for local connections
#16 3.026 initdb: hint: You can change this by editing pg_hba.conf or using the option -A, or --auth-local and --auth-host, the next time you run initdb.
#16 3.082 waiting for server to start....2025-02-13 00:26:52.054 UTC [42] LOG:  starting PostgreSQL 16.6 on x86_64-pc-linux-musl, compiled by gcc (Alpine 14.2.0) 14.2.0, 64-bit
#16 3.121 2025-02-13 00:26:52.057 UTC [42] LOG:  listening on Unix socket "/var/run/postgresql/.s.PGSQL.5432"
#16 3.129 2025-02-13 00:26:52.064 UTC [45] LOG:  database system was shut down at 2025-02-13 00:26:50 UTC
#16 3.138 2025-02-13 00:26:52.073 UTC [42] LOG:  database system is ready to accept connections
#16 3.183  done
#16 3.183 server started
#16 3.341 CREATE DATABASE
#16 3.342
#16 3.343
#16 3.344 /usr/local/bin/docker-entrypoint.sh: sourcing /docker-entrypoint-initdb.d/1-load_data.sh
#16 3.352 ----------------------------------------
#16 3.352       Creating Postgis extensions
#16 3.352 ----------------------------------------
#16 4.180 CREATE EXTENSION
#16 4.206 CREATE EXTENSION
#16 4.912 CREATE EXTENSION
#16 4.940 CREATE EXTENSION
#16 4.941 ----------------------------------------
#16 4.941       Adding US national data
#16 4.941 ----------------------------------------
#16 4.958 ALTER SYSTEM
#16 4.982 ALTER SYSTEM
#16 5.002 ALTER SYSTEM
#16 5.015 NOTICE:  schema "tiger_staging" does not exist, skipping
#16 5.015 DROP SCHEMA
#16 5.035 CREATE SCHEMA
#16 5.079 CREATE TABLE
#16 5.094 Field aland is an FTDouble with width 14 and precision 0
#16 5.094 Field awater is an FTDouble with width 14 and precision 0
#16 5.094 Shapefile type: Polygon
#16 5.094 Postgis type: MULTIPOLYGON[2]
#16 5.097 SET
#16 5.097 SET
#16 5.097 BEGIN
#16 5.103 CREATE TABLE
#16 5.108 ALTER TABLE
#16 5.134                         addgeometrycolumn
#16 5.134 ------------------------------------------------------------------
#16 5.134  tiger_staging.state.the_geom SRID:4269 TYPE:MULTIPOLYGON DIMS:2
#16 5.134 (1 row)
#16 5.134
#16 6.153 COPY 56
#16 6.159 COMMIT
#16 6.166 ANALYZE
#16 6.229 NOTICE:  INSERT INTO tiger_data.state_all(aland,awater,division,funcstat,intptlat,intptlon,lsad,mtfcc,name,region,statefp,statens,stusps,the_geom) SELECT aland,awater,division,funcstat,intptlat,intptlon,lsad,mtfcc,name,region,statefp,statens,stusps,the_geom FROM tiger_staging.state;
#16 6.704  loader_load_staged_data
#16 6.704 -------------------------
#16 6.704                       56
#16 6.704 (1 row)
#16 6.704
#16 6.743 CREATE INDEX
#16 6.792 VACUUM
#16 6.814 DROP SCHEMA
#16 6.831 CREATE SCHEMA
#16 6.864 CREATE TABLE
#16 6.882 Field aland is an FTDouble with width 14 and precision 0
#16 6.882 Field awater is an FTDouble with width 14 and precision 0
#16 6.882 Shapefile type: Polygon
#16 6.882 Postgis type: MULTIPOLYGON[2]
#16 6.882 SET
#16 6.882 SET
#16 6.882 BEGIN
#16 6.889 CREATE TABLE
#16 6.893 ALTER TABLE
#16 6.916                          addgeometrycolumn
#16 6.916 -------------------------------------------------------------------
#16 6.916  tiger_staging.county.the_geom SRID:4269 TYPE:MULTIPOLYGON DIMS:2
#16 6.916 (1 row)
#16 6.916
#16 11.52 COPY 3234
#16 11.53 COMMIT
#16 11.68 ANALYZE
#16 11.73 NOTICE:  INSERT INTO tiger_data.county_all(aland,awater,cbsafp,classfp,cntyidfp,countyfp,countyns,csafp,funcstat,intptlat,intptlon,lsad,metdivfp,mtfcc,name,namelsad,statefp,the_geom) SELECT aland,awater,cbsafp,classfp,cntyidfp,countyfp,countyns,csafp,funcstat,intptlat,intptlon,lsad,metdivfp,mtfcc,name,namelsad,statefp,the_geom FROM tiger_staging.county;
#16 15.42 ALTER TABLE
#16 15.42  loader_load_staged_data
#16 15.42 -------------------------
#16 15.42                     3234
#16 15.42 (1 row)
#16 15.42
#16 15.53 CREATE INDEX
#16 15.57 CREATE INDEX
#16 15.60 CREATE TABLE
#16 15.85 VACUUM
#16 15.93 INSERT 0 3234
#16 15.96 VACUUM
#16 15.97 ----------------------------------------
#16 15.97       Loading state data for: 'AS 60'
#16 15.97 ----------------------------------------
#16 16.00 DROP SCHEMA
#16 16.02 CREATE SCHEMA
#16 16.05 CREATE TABLE
#16 16.06 Field aland is an FTDouble with width 14 and precision 0
#16 16.06 Field awater is an FTDouble with width 14 and precision 0
#16 16.06 Shapefile type: Polygon
#16 16.06 Postgis type: MULTIPOLYGON[2]
#16 16.06 SET
#16 16.06 SET
#16 16.06 BEGIN
#16 16.07 CREATE TABLE
#16 16.07 ALTER TABLE
#16 16.09                           addgeometrycolumn
#16 16.09 ---------------------------------------------------------------------
#16 16.09  tiger_staging.as_place.the_geom SRID:4269 TYPE:MULTIPOLYGON DIMS:2
#16 16.09 (1 row)
#16 16.09
#16 16.10 COPY 77
#16 16.11 COMMIT
#16 16.11 ANALYZE
#16 16.15 NOTICE:  INSERT INTO tiger_data.as_place(aland,awater,classfp,funcstat,intptlat,intptlon,lsad,mtfcc,name,namelsad,pcicbsa,placefp,placens,plcidfp,statefp,the_geom) SELECT aland,awater,classfp,funcstat,intptlat,intptlon,lsad,mtfcc,name,namelsad,pcicbsa,placefp,placens,plcidfp,statefp,the_geom FROM tiger_staging.as_place;
#16 16.18 ALTER TABLE
#16 16.18  loader_load_staged_data
#16 16.18 -------------------------
#16 16.18                       77
#16 16.18 (1 row)
#16 16.18
#16 16.18 ALTER TABLE
#16 16.20 CREATE INDEX
#16 16.24 CREATE INDEX
#16 16.26 ALTER TABLE
#16 16.29 DROP SCHEMA
#16 16.31 CREATE SCHEMA
#16 16.33 CREATE TABLE
#16 16.35 Field aland is an FTDouble with width 14 and precision 0
#16 16.35 Field awater is an FTDouble with width 14 and precision 0
#16 16.35 Shapefile type: Polygon
#16 16.35 Postgis type: MULTIPOLYGON[2]
#16 16.35 SET
#16 16.35 SET
#16 16.35 BEGIN
#16 16.36 CREATE TABLE
#16 16.36 ALTER TABLE
#16 16.40                           addgeometrycolumn
#16 16.40 ----------------------------------------------------------------------
#16 16.40  tiger_staging.as_cousub.the_geom SRID:4269 TYPE:MULTIPOLYGON DIMS:2
#16 16.40 (1 row)
#16 16.40
#16 16.41 COPY 16
#16 16.41 COMMIT
#16 16.41 ANALYZE
#16 16.46 NOTICE:  INSERT INTO tiger_data.as_cousub(aland,awater,classfp,cosbidfp,countyfp,cousubfp,cousubns,funcstat,intptlat,intptlon,lsad,mtfcc,name,namelsad,statefp,the_geom) SELECT aland,awater,classfp,cosbidfp,countyfp,cousubfp,cousubns,funcstat,intptlat,intptlon,lsad,mtfcc,name,namelsad,statefp,the_geom FROM tiger_staging.as_cousub;
#16 16.47 ALTER TABLE
#16 16.47  loader_load_staged_data
#16 16.47 -------------------------
#16 16.47                       16
#16 16.47 (1 row)
#16 16.47
#16 16.47 ALTER TABLE
#16 16.51 CREATE INDEX
#16 16.54 CREATE INDEX
#16 16.56 DROP SCHEMA
#16 16.58 CREATE SCHEMA
#16 16.61 CREATE TABLE
#16 16.63 Field aland is an FTDouble with width 14 and precision 0
#16 16.63 Field awater is an FTDouble with width 14 and precision 0
#16 16.63 Shapefile type: Polygon
#16 16.63 Postgis type: MULTIPOLYGON[2]
#16 16.63 SET
#16 16.63 SET
#16 16.63 BEGIN
#16 16.63 CREATE TABLE
#16 16.64 ALTER TABLE
#16 16.66                           addgeometrycolumn
#16 16.66 ---------------------------------------------------------------------
#16 16.66  tiger_staging.as_tract.the_geom SRID:4269 TYPE:MULTIPOLYGON DIMS:2
#16 16.66 (1 row)
#16 16.66
#16 16.66 COPY 18
#16 16.66 COMMIT
#16 16.67 ANALYZE
#16 16.71 NOTICE:  INSERT INTO tiger_data.as_tract(aland,awater,countyfp,funcstat,intptlat,intptlon,mtfcc,name,namelsad,statefp,the_geom,tract_id,tractce) SELECT aland,awater,countyfp,funcstat,intptlat,intptlon,mtfcc,name,namelsad,statefp,the_geom,tract_id,tractce FROM tiger_staging.as_tract;
#16 16.73 ALTER TABLE
#16 16.73  loader_load_staged_data
#16 16.73 -------------------------
#16 16.73                       18
#16 16.73 (1 row)
#16 16.73
#16 16.77 CREATE INDEX
#16 16.80 VACUUM
#16 16.83 ALTER TABLE
#16 16.85 DROP SCHEMA
#16 16.86 CREATE SCHEMA
#16 16.89 CREATE TABLE
#16 16.91 Field tfid is an FTDouble with width 10 and precision 0
#16 16.91 Field atotal is an FTDouble with width 14 and precision 0
#16 16.91 Shapefile type: Polygon
#16 16.91 Postgis type: MULTIPOLYGON[2]
#16 16.91 SET
#16 16.91 SET
#16 16.91 BEGIN
#16 16.91 CREATE TABLE
#16 16.92 ALTER TABLE
#16 16.94                           addgeometrycolumn
#16 16.94 ---------------------------------------------------------------------
#16 16.94  tiger_staging.as_faces.the_geom SRID:4269 TYPE:MULTIPOLYGON DIMS:2
#16 16.94 (1 row)
#16 16.94
#16 17.00 COPY 753
#16 17.00 COMMIT
#16 17.01 ANALYZE
#16 17.06 NOTICE:  INSERT INTO tiger_data.as_faces(aiannhce,aiannhfp,anrcfp,atotal,blkgrpce,blkgrpce20,blockce20,cbsafp,cd111fp,comptyp,conctyfp,countyfp,countyfp20,cousubfp,csafp,elsdlea,intptlat,intptlon,lwflag,metdivfp,"offset",placefp,scsdlea,sldlst,sldust,statefp,statefp20,submcdfp,tblkgpce,tfid,the_geom,tractce,tractce20,trsubce,trsubfp,ttractce,unsdlea,zcta5ce) SELECT aiannhce,aiannhfp,anrcfp,atotal,blkgrpce,blkgrpce20,blockce20,cbsafp,cd118fp,comptyp,conctyfp,countyfp,countyfp20,cousubfp,csafp,elsdlea,intptlat,intptlon,lwflag,metdivfp,"offset",placefp,scsdlea,sldlst,sldust,statefp,statefp20,submcdfp,tblkgpce,tfid,the_geom,tractce,tractce20,trsubce,trsubfp,ttractce,unsdlea,zcta5ce20 FROM tiger_staging.as_faces;
#16 17.09  loader_load_staged_data
#16 17.09 -------------------------
#16 17.09                      753
#16 17.09 (1 row)
#16 17.09
#16 17.11 Field tfid is an FTDouble with width 10 and precision 0
#16 17.11 Field atotal is an FTDouble with width 14 and precision 0
#16 17.11 Shapefile type: Polygon
#16 17.11 Postgis type: MULTIPOLYGON[2]
#16 17.11 SET
#16 17.11 SET
#16 17.11 BEGIN
#16 17.12 CREATE TABLE
#16 17.12 ALTER TABLE
#16 17.14                           addgeometrycolumn
#16 17.14 ---------------------------------------------------------------------
#16 17.14  tiger_staging.as_faces.the_geom SRID:4269 TYPE:MULTIPOLYGON DIMS:2
#16 17.14 (1 row)
#16 17.14
#16 17.16 COPY 108
#16 17.17 COMMIT
#16 17.17 ANALYZE
#16 17.21 NOTICE:  INSERT INTO tiger_data.as_faces(aiannhce,aiannhfp,anrcfp,atotal,blkgrpce,blkgrpce20,blockce20,cbsafp,cd111fp,comptyp,conctyfp,countyfp,countyfp20,cousubfp,csafp,elsdlea,intptlat,intptlon,lwflag,metdivfp,"offset",placefp,scsdlea,sldlst,sldust,statefp,statefp20,submcdfp,tblkgpce,tfid,the_geom,tractce,tractce20,trsubce,trsubfp,ttractce,unsdlea,zcta5ce) SELECT aiannhce,aiannhfp,anrcfp,atotal,blkgrpce,blkgrpce20,blockce20,cbsafp,cd118fp,comptyp,conctyfp,countyfp,countyfp20,cousubfp,csafp,elsdlea,intptlat,intptlon,lwflag,metdivfp,"offset",placefp,scsdlea,sldlst,sldust,statefp,statefp20,submcdfp,tblkgpce,tfid,the_geom,tractce,tractce20,trsubce,trsubfp,ttractce,unsdlea,zcta5ce20 FROM tiger_staging.as_faces;
#16 17.24  loader_load_staged_data
#16 17.24 -------------------------
#16 17.24                      108
#16 17.24 (1 row)
#16 17.24
#16 17.26 Field tfid is an FTDouble with width 10 and precision 0
#16 17.26 Field atotal is an FTDouble with width 14 and precision 0
#16 17.26 Shapefile type: Polygon
#16 17.26 Postgis type: MULTIPOLYGON[2]
#16 17.26 SET
#16 17.26 SET
#16 17.26 BEGIN
#16 17.27 CREATE TABLE
#16 17.27 ALTER TABLE
#16 17.30                           addgeometrycolumn
#16 17.30 ---------------------------------------------------------------------
#16 17.30  tiger_staging.as_faces.the_geom SRID:4269 TYPE:MULTIPOLYGON DIMS:2
#16 17.30 (1 row)
#16 17.30
#16 17.30 COPY 4
#16 17.30 COMMIT
#16 17.30 ANALYZE
#16 17.35 NOTICE:  INSERT INTO tiger_data.as_faces(aiannhce,aiannhfp,anrcfp,atotal,blkgrpce,blkgrpce20,blockce20,cbsafp,cd111fp,comptyp,conctyfp,countyfp,countyfp20,cousubfp,csafp,elsdlea,intptlat,intptlon,lwflag,metdivfp,"offset",placefp,scsdlea,sldlst,sldust,statefp,statefp20,submcdfp,tblkgpce,tfid,the_geom,tractce,tractce20,trsubce,trsubfp,ttractce,unsdlea,zcta5ce) SELECT aiannhce,aiannhfp,anrcfp,atotal,blkgrpce,blkgrpce20,blockce20,cbsafp,cd118fp,comptyp,conctyfp,countyfp,countyfp20,cousubfp,csafp,elsdlea,intptlat,intptlon,lwflag,metdivfp,"offset",placefp,scsdlea,sldlst,sldust,statefp,statefp20,submcdfp,tblkgpce,tfid,the_geom,tractce,tractce20,trsubce,trsubfp,ttractce,unsdlea,zcta5ce20 FROM tiger_staging.as_faces;
#16 17.37  loader_load_staged_data
#16 17.37 -------------------------
#16 17.37                        4
#16 17.37 (1 row)
#16 17.37
#16 17.39 Field tfid is an FTDouble with width 10 and precision 0
#16 17.39 Field atotal is an FTDouble with width 14 and precision 0
#16 17.39 Shapefile type: Polygon
#16 17.39 Postgis type: MULTIPOLYGON[2]
#16 17.39 SET
#16 17.39 SET
#16 17.39 BEGIN
#16 17.39 CREATE TABLE
#16 17.40 ALTER TABLE
#16 17.42                           addgeometrycolumn
#16 17.42 ---------------------------------------------------------------------
#16 17.42  tiger_staging.as_faces.the_geom SRID:4269 TYPE:MULTIPOLYGON DIMS:2
#16 17.42 (1 row)
#16 17.42
#16 17.42 COPY 6
#16 17.42 COMMIT
#16 17.42 ANALYZE
#16 17.47 NOTICE:  INSERT INTO tiger_data.as_faces(aiannhce,aiannhfp,anrcfp,atotal,blkgrpce,blkgrpce20,blockce20,cbsafp,cd111fp,comptyp,conctyfp,countyfp,countyfp20,cousubfp,csafp,elsdlea,intptlat,intptlon,lwflag,metdivfp,"offset",placefp,scsdlea,sldlst,sldust,statefp,statefp20,submcdfp,tblkgpce,tfid,the_geom,tractce,tractce20,trsubce,trsubfp,ttractce,unsdlea,zcta5ce) SELECT aiannhce,aiannhfp,anrcfp,atotal,blkgrpce,blkgrpce20,blockce20,cbsafp,cd118fp,comptyp,conctyfp,countyfp,countyfp20,cousubfp,csafp,elsdlea,intptlat,intptlon,lwflag,metdivfp,"offset",placefp,scsdlea,sldlst,sldust,statefp,statefp20,submcdfp,tblkgpce,tfid,the_geom,tractce,tractce20,trsubce,trsubfp,ttractce,unsdlea,zcta5ce20 FROM tiger_staging.as_faces;
#16 17.49  loader_load_staged_data
#16 17.49 -------------------------
#16 17.49                        6
#16 17.49 (1 row)
#16 17.49
#16 17.51 Field tfid is an FTDouble with width 10 and precision 0
#16 17.51 Field atotal is an FTDouble with width 14 and precision 0
#16 17.51 Shapefile type: Polygon
#16 17.51 Postgis type: MULTIPOLYGON[2]
#16 17.51 SET
#16 17.51 SET
#16 17.51 BEGIN
#16 17.52 CREATE TABLE
#16 17.52 ALTER TABLE
#16 17.54                           addgeometrycolumn
#16 17.54 ---------------------------------------------------------------------
#16 17.54  tiger_staging.as_faces.the_geom SRID:4269 TYPE:MULTIPOLYGON DIMS:2
#16 17.54 (1 row)
#16 17.54
#16 17.60 COPY 707
#16 17.60 COMMIT
#16 17.62 ANALYZE
#16 17.66 NOTICE:  INSERT INTO tiger_data.as_faces(aiannhce,aiannhfp,anrcfp,atotal,blkgrpce,blkgrpce20,blockce20,cbsafp,cd111fp,comptyp,conctyfp,countyfp,countyfp20,cousubfp,csafp,elsdlea,intptlat,intptlon,lwflag,metdivfp,"offset",placefp,scsdlea,sldlst,sldust,statefp,statefp20,submcdfp,tblkgpce,tfid,the_geom,tractce,tractce20,trsubce,trsubfp,ttractce,unsdlea,zcta5ce) SELECT aiannhce,aiannhfp,anrcfp,atotal,blkgrpce,blkgrpce20,blockce20,cbsafp,cd118fp,comptyp,conctyfp,countyfp,countyfp20,cousubfp,csafp,elsdlea,intptlat,intptlon,lwflag,metdivfp,"offset",placefp,scsdlea,sldlst,sldust,statefp,statefp20,submcdfp,tblkgpce,tfid,the_geom,tractce,tractce20,trsubce,trsubfp,ttractce,unsdlea,zcta5ce20 FROM tiger_staging.as_faces;
#16 17.70  loader_load_staged_data
#16 17.70 -------------------------
#16 17.70                      707
#16 17.70 (1 row)
#16 17.70
#16 17.74 CREATE INDEX
#16 17.77 CREATE INDEX
#16 17.80 CREATE INDEX
#16 17.83 ALTER TABLE
#16 17.89 VACUUM
#16 17.91 DROP SCHEMA
#16 17.93 CREATE SCHEMA
#16 17.95 CREATE TABLE
#16 17.95 ALTER TABLE
#16 17.97 Unable to open tl_2020_60010_featnames.shp or tl_2020_60010_featnames.SHP.
#16 17.97 Field tlid is an FTDouble with width 10 and precision 0
#16 17.97 tl_2020_60010_featnames.dbf: shape (.shp) or index files (.shx) can not be opened, will just import attribute data.
#16 17.97 SET
#16 17.97 SET
#16 17.97 BEGIN
#16 17.98 CREATE TABLE
#16 17.98 ALTER TABLE
#16 18.02 COPY 2298
#16 18.02 COMMIT
#16 18.03 ANALYZE
#16 18.07 NOTICE:  INSERT INTO tiger_data.as_featnames(fullname,linearid,mtfcc,name,paflag,predir,predirabrv,prequal,prequalabr,pretyp,pretypabrv,sufdir,sufdirabrv,sufqual,sufqualabr,suftyp,suftypabrv,tlid) SELECT fullname,linearid,mtfcc,name,paflag,predir,predirabrv,prequal,prequalabr,pretyp,pretypabrv,sufdir,sufdirabrv,sufqual,sufqualabr,suftyp,suftypabrv,tlid FROM tiger_staging.as_featnames;
#16 18.09  loader_load_staged_data
#16 18.09 -------------------------
#16 18.09                     2298
#16 18.09 (1 row)
#16 18.09
#16 18.11 Unable to open tl_2020_60020_featnames.shp or tl_2020_60020_featnames.SHP.
#16 18.11 Field tlid is an FTDouble with width 10 and precision 0
#16 18.11 tl_2020_60020_featnames.dbf: shape (.shp) or index files (.shx) can not be opened, will just import attribute data.
#16 18.11 SET
#16 18.11 SET
#16 18.11 BEGIN
#16 18.11 CREATE TABLE
#16 18.12 ALTER TABLE
#16 18.12 COPY 348
#16 18.12 COMMIT
#16 18.13 ANALYZE
#16 18.17 NOTICE:  INSERT INTO tiger_data.as_featnames(fullname,linearid,mtfcc,name,paflag,predir,predirabrv,prequal,prequalabr,pretyp,pretypabrv,sufdir,sufdirabrv,sufqual,sufqualabr,suftyp,suftypabrv,tlid) SELECT fullname,linearid,mtfcc,name,paflag,predir,predirabrv,prequal,prequalabr,pretyp,pretypabrv,sufdir,sufdirabrv,sufqual,sufqualabr,suftyp,suftypabrv,tlid FROM tiger_staging.as_featnames;
#16 18.18  loader_load_staged_data
#16 18.18 -------------------------
#16 18.18                      348
#16 18.18 (1 row)
#16 18.18
#16 18.20 Unable to open tl_2020_60030_featnames.shp or tl_2020_60030_featnames.SHP.
#16 18.20 Field tlid is an FTDouble with width 10 and precision 0
#16 18.20 tl_2020_60030_featnames.dbf: shape (.shp) or index files (.shx) can not be opened, will just import attribute data.
#16 18.20 SET
#16 18.20 SET
#16 18.20 BEGIN
#16 18.20 CREATE TABLE
#16 18.21 ALTER TABLE
#16 18.21 COPY 2
#16 18.21 COMMIT
#16 18.21 ANALYZE
#16 18.25 NOTICE:  INSERT INTO tiger_data.as_featnames(fullname,linearid,mtfcc,name,paflag,predir,predirabrv,prequal,prequalabr,pretyp,pretypabrv,sufdir,sufdirabrv,sufqual,sufqualabr,suftyp,suftypabrv,tlid) SELECT fullname,linearid,mtfcc,name,paflag,predir,predirabrv,prequal,prequalabr,pretyp,pretypabrv,sufdir,sufdirabrv,sufqual,sufqualabr,suftyp,suftypabrv,tlid FROM tiger_staging.as_featnames;
#16 18.26  loader_load_staged_data
#16 18.26 -------------------------
#16 18.26                        2
#16 18.26 (1 row)
#16 18.26
#16 18.28 Unable to open tl_2020_60040_featnames.shp or tl_2020_60040_featnames.SHP.
#16 18.28 Field tlid is an FTDouble with width 10 and precision 0
#16 18.28 tl_2020_60040_featnames.dbf: shape (.shp) or index files (.shx) can not be opened, will just import attribute data.
#16 18.28 SET
#16 18.28 SET
#16 18.28 BEGIN
#16 18.28 CREATE TABLE
#16 18.29 ALTER TABLE
#16 18.29 COPY 2
#16 18.29 COMMIT
#16 18.29 ANALYZE
#16 18.34 NOTICE:  INSERT INTO tiger_data.as_featnames(fullname,linearid,mtfcc,name,paflag,predir,predirabrv,prequal,prequalabr,pretyp,pretypabrv,sufdir,sufdirabrv,sufqual,sufqualabr,suftyp,suftypabrv,tlid) SELECT fullname,linearid,mtfcc,name,paflag,predir,predirabrv,prequal,prequalabr,pretyp,pretypabrv,sufdir,sufdirabrv,sufqual,sufqualabr,suftyp,suftypabrv,tlid FROM tiger_staging.as_featnames;
#16 18.34  loader_load_staged_data
#16 18.34 -------------------------
#16 18.34                        2
#16 18.34 (1 row)
#16 18.34
#16 18.36 Unable to open tl_2020_60050_featnames.shp or tl_2020_60050_featnames.SHP.
#16 18.36 Field tlid is an FTDouble with width 10 and precision 0
#16 18.36 tl_2020_60050_featnames.dbf: shape (.shp) or index files (.shx) can not be opened, will just import attribute data.
#16 18.36 SET
#16 18.36 SET
#16 18.36 BEGIN
#16 18.37 CREATE TABLE
#16 18.37 ALTER TABLE
#16 18.43 COPY 3678
#16 18.43 COMMIT
#16 18.44 ANALYZE
#16 18.49 NOTICE:  INSERT INTO tiger_data.as_featnames(fullname,linearid,mtfcc,name,paflag,predir,predirabrv,prequal,prequalabr,pretyp,pretypabrv,sufdir,sufdirabrv,sufqual,sufqualabr,suftyp,suftypabrv,tlid) SELECT fullname,linearid,mtfcc,name,paflag,predir,predirabrv,prequal,prequalabr,pretyp,pretypabrv,sufdir,sufdirabrv,sufqual,sufqualabr,suftyp,suftypabrv,tlid FROM tiger_staging.as_featnames;
#16 18.50  loader_load_staged_data
#16 18.50 -------------------------
#16 18.50                     3678
#16 18.50 (1 row)
#16 18.50
#16 18.54 CREATE INDEX
#16 18.56 CREATE INDEX
#16 18.59 CREATE INDEX
#16 18.61 ALTER TABLE
#16 18.67 VACUUM
#16 18.69 DROP SCHEMA
#16 18.71 CREATE SCHEMA
#16 18.74 CREATE TABLE
#16 18.76 Field tlid is an FTDouble with width 10 and precision 0
#16 18.76 Field tfidl is an FTDouble with width 10 and precision 0
#16 18.76 Field tfidr is an FTDouble with width 10 and precision 0
#16 18.76 Field tnidf is an FTDouble with width 10 and precision 0
#16 18.76 Field tnidt is an FTDouble with width 10 and precision 0
#16 18.76 Shapefile type: Arc
#16 18.76 Postgis type: MULTILINESTRING[2]
#16 18.76 SET
#16 18.76 SET
#16 18.76 BEGIN
#16 18.76 CREATE TABLE
#16 18.76 ALTER TABLE
#16 18.79                            addgeometrycolumn
#16 18.79 ------------------------------------------------------------------------
#16 18.79  tiger_staging.as_edges.the_geom SRID:4269 TYPE:MULTILINESTRING DIMS:2
#16 18.79 (1 row)
#16 18.79
#16 18.93 COPY 3142
#16 18.93 COMMIT
#16 18.97 ANALYZE
#16 19.01 NOTICE:  INSERT INTO tiger_data.as_edges(artpath,countyfp,deckedroad,exttyp,featcat,fullname,gcseflg,hydroflg,lfromadd,ltoadd,mtfcc,offsetl,offsetr,olfflg,passflg,persist,railflg,rfromadd,roadflg,rtoadd,smid,statefp,tfidl,tfidr,the_geom,tlid,tnidf,tnidt,ttyp,zipl,zipr) SELECT artpath,countyfp,deckedroad,exttyp,featcat,fullname,gcseflg,hydroflg,lfromadd,ltoadd,mtfcc,offsetl,offsetr,olfflg,passflg,persist,railflg,rfromadd,roadflg,rtoadd,smid,statefp,tfidl,tfidr,the_geom,tlid,tnidf,tnidt,ttyp,zipl,zipr FROM tiger_staging.as_edges;
#16 19.05  loader_load_staged_data
#16 19.05 -------------------------
#16 19.05                     3142
#16 19.05 (1 row)
#16 19.05
#16 19.07 Field tlid is an FTDouble with width 10 and precision 0
#16 19.07 Field tfidl is an FTDouble with width 10 and precision 0
#16 19.07 Field tfidr is an FTDouble with width 10 and precision 0
#16 19.07 Field tnidf is an FTDouble with width 10 and precision 0
#16 19.07 Field tnidt is an FTDouble with width 10 and precision 0
#16 19.07 Shapefile type: Arc
#16 19.07 Postgis type: MULTILINESTRING[2]
#16 19.07 SET
#16 19.07 SET
#16 19.07 BEGIN
#16 19.08 CREATE TABLE
#16 19.08 ALTER TABLE
#16 19.10                            addgeometrycolumn
#16 19.10 ------------------------------------------------------------------------
#16 19.10  tiger_staging.as_edges.the_geom SRID:4269 TYPE:MULTILINESTRING DIMS:2
#16 19.10 (1 row)
#16 19.10
#16 19.13 COPY 456
#16 19.13 COMMIT
#16 19.14 ANALYZE
#16 19.19 NOTICE:  INSERT INTO tiger_data.as_edges(artpath,countyfp,deckedroad,exttyp,featcat,fullname,gcseflg,hydroflg,lfromadd,ltoadd,mtfcc,offsetl,offsetr,olfflg,passflg,persist,railflg,rfromadd,roadflg,rtoadd,smid,statefp,tfidl,tfidr,the_geom,tlid,tnidf,tnidt,ttyp,zipl,zipr) SELECT artpath,countyfp,deckedroad,exttyp,featcat,fullname,gcseflg,hydroflg,lfromadd,ltoadd,mtfcc,offsetl,offsetr,olfflg,passflg,persist,railflg,rfromadd,roadflg,rtoadd,smid,statefp,tfidl,tfidr,the_geom,tlid,tnidf,tnidt,ttyp,zipl,zipr FROM tiger_staging.as_edges;
#16 19.21  loader_load_staged_data
#16 19.21 -------------------------
#16 19.21                      456
#16 19.21 (1 row)
#16 19.21
#16 19.23 Field tlid is an FTDouble with width 10 and precision 0
#16 19.23 Field tfidl is an FTDouble with width 10 and precision 0
#16 19.23 Field tfidr is an FTDouble with width 10 and precision 0
#16 19.23 Field tnidf is an FTDouble with width 10 and precision 0
#16 19.23 Field tnidt is an FTDouble with width 10 and precision 0
#16 19.23 Shapefile type: Arc
#16 19.23 Postgis type: MULTILINESTRING[2]
#16 19.23 SET
#16 19.23 SET
#16 19.23 BEGIN
#16 19.24 CREATE TABLE
#16 19.24 ALTER TABLE
#16 19.27                            addgeometrycolumn
#16 19.27 ------------------------------------------------------------------------
#16 19.27  tiger_staging.as_edges.the_geom SRID:4269 TYPE:MULTILINESTRING DIMS:2
#16 19.27 (1 row)
#16 19.27
#16 19.27 COPY 4
#16 19.28 COMMIT
#16 19.28 ANALYZE
#16 19.32 NOTICE:  INSERT INTO tiger_data.as_edges(artpath,countyfp,deckedroad,exttyp,featcat,fullname,gcseflg,hydroflg,lfromadd,ltoadd,mtfcc,offsetl,offsetr,olfflg,passflg,persist,railflg,rfromadd,roadflg,rtoadd,smid,statefp,tfidl,tfidr,the_geom,tlid,tnidf,tnidt,ttyp,zipl,zipr) SELECT artpath,countyfp,deckedroad,exttyp,featcat,fullname,gcseflg,hydroflg,lfromadd,ltoadd,mtfcc,offsetl,offsetr,olfflg,passflg,persist,railflg,rfromadd,roadflg,rtoadd,smid,statefp,tfidl,tfidr,the_geom,tlid,tnidf,tnidt,ttyp,zipl,zipr FROM tiger_staging.as_edges;
#16 19.34  loader_load_staged_data
#16 19.34 -------------------------
#16 19.34                        4
#16 19.34 (1 row)
#16 19.34
#16 19.36 Field tlid is an FTDouble with width 10 and precision 0
#16 19.36 Field tfidl is an FTDouble with width 10 and precision 0
#16 19.36 Field tfidr is an FTDouble with width 10 and precision 0
#16 19.36 Field tnidf is an FTDouble with width 10 and precision 0
#16 19.36 Field tnidt is an FTDouble with width 10 and precision 0
#16 19.36 Shapefile type: Arc
#16 19.36 Postgis type: MULTILINESTRING[2]
#16 19.36 SET
#16 19.36 SET
#16 19.36 BEGIN
#16 19.37 CREATE TABLE
#16 19.38 ALTER TABLE
#16 19.39                            addgeometrycolumn
#16 19.39 ------------------------------------------------------------------------
#16 19.39  tiger_staging.as_edges.the_geom SRID:4269 TYPE:MULTILINESTRING DIMS:2
#16 19.39 (1 row)
#16 19.39
#16 19.40 COPY 8
#16 19.40 COMMIT
#16 19.40 ANALYZE
#16 19.45 NOTICE:  INSERT INTO tiger_data.as_edges(artpath,countyfp,deckedroad,exttyp,featcat,fullname,gcseflg,hydroflg,lfromadd,ltoadd,mtfcc,offsetl,offsetr,olfflg,passflg,persist,railflg,rfromadd,roadflg,rtoadd,smid,statefp,tfidl,tfidr,the_geom,tlid,tnidf,tnidt,ttyp,zipl,zipr) SELECT artpath,countyfp,deckedroad,exttyp,featcat,fullname,gcseflg,hydroflg,lfromadd,ltoadd,mtfcc,offsetl,offsetr,olfflg,passflg,persist,railflg,rfromadd,roadflg,rtoadd,smid,statefp,tfidl,tfidr,the_geom,tlid,tnidf,tnidt,ttyp,zipl,zipr FROM tiger_staging.as_edges;
#16 19.46  loader_load_staged_data
#16 19.46 -------------------------
#16 19.46                        8
#16 19.46 (1 row)
#16 19.46
#16 19.48 Field tlid is an FTDouble with width 10 and precision 0
#16 19.48 Field tfidl is an FTDouble with width 10 and precision 0
#16 19.48 Field tfidr is an FTDouble with width 10 and precision 0
#16 19.48 Field tnidf is an FTDouble with width 10 and precision 0
#16 19.48 Field tnidt is an FTDouble with width 10 and precision 0
#16 19.48 Shapefile type: Arc
#16 19.48 Postgis type: MULTILINESTRING[2]
#16 19.48 SET
#16 19.48 SET
#16 19.48 BEGIN
#16 19.49 CREATE TABLE
#16 19.50 ALTER TABLE
#16 19.51                            addgeometrycolumn
#16 19.51 ------------------------------------------------------------------------
#16 19.51  tiger_staging.as_edges.the_geom SRID:4269 TYPE:MULTILINESTRING DIMS:2
#16 19.51 (1 row)
#16 19.51
#16 19.71 COPY 4491
#16 19.71 COMMIT
#16 19.75 ANALYZE
#16 19.79 NOTICE:  INSERT INTO tiger_data.as_edges(artpath,countyfp,deckedroad,exttyp,featcat,fullname,gcseflg,hydroflg,lfromadd,ltoadd,mtfcc,offsetl,offsetr,olfflg,passflg,persist,railflg,rfromadd,roadflg,rtoadd,smid,statefp,tfidl,tfidr,the_geom,tlid,tnidf,tnidt,ttyp,zipl,zipr) SELECT artpath,countyfp,deckedroad,exttyp,featcat,fullname,gcseflg,hydroflg,lfromadd,ltoadd,mtfcc,offsetl,offsetr,olfflg,passflg,persist,railflg,rfromadd,roadflg,rtoadd,smid,statefp,tfidl,tfidr,the_geom,tlid,tnidf,tnidt,ttyp,zipl,zipr FROM tiger_staging.as_edges;
#16 19.85  loader_load_staged_data
#16 19.85 -------------------------
#16 19.85                     4491
#16 19.85 (1 row)
#16 19.85
#16 19.88 ALTER TABLE
#16 19.91 CREATE INDEX
#16 19.98 CREATE INDEX
#16 20.02 CREATE INDEX
#16 20.05 CREATE INDEX
#16 20.10 CREATE INDEX
#16 20.14 CREATE INDEX
#16 20.17 CREATE TABLE
#16 20.21 INSERT 0 0
#16 20.24 CREATE INDEX
#16 20.26 ALTER TABLE
#16 20.37 VACUUM
#16 20.39 VACUUM
#16 20.42 CREATE TABLE
#16 20.44 INSERT 0 0
#16 20.46 ALTER TABLE
#16 20.48 CREATE INDEX
#16 20.50 DROP SCHEMA
#16 20.51 CREATE SCHEMA
#16 20.54 CREATE TABLE
#16 20.54 ALTER TABLE
#16 20.56 Unable to open *addr*.shp or *addr*.SHP.
#16 20.56 *addr*.dbf: dbf file (.dbf) can not be opened.
#16 ERROR: process "/bin/bash -c docker-entrypoint.sh postgres" did not complete successfully: exit code: 1
------
 > [buildtime_init_builder 9/9] RUN docker-entrypoint.sh postgres:
20.42 CREATE TABLE
20.44 INSERT 0 0
20.46 ALTER TABLE
20.48 CREATE INDEX
20.50 DROP SCHEMA
20.51 CREATE SCHEMA
20.54 CREATE TABLE
20.54 ALTER TABLE
20.56 Unable to open *addr*.shp or *addr*.SHP.
20.56 *addr*.dbf: dbf file (.dbf) can not be opened.

```


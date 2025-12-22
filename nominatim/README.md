


## Example Use of Nominatim Geocoding

Search API is documented here:
https://nominatim.org/release-docs/latest/api/Search/

Example Use:

```

curl 'http:/127.0.0.1:50003/search?q=1410+NE+Campus+Parkway%2c+Seattle%2c+WA+98195&addressdetails=1&format=json'


[{'place_id': 20461221,
  'licence': 'Data © OpenStreetMap contributors, ODbL 1.0. https://osm.org/copyright',
  'osm_type': 'node',
  'osm_id': 6023667700,
  'boundingbox': ['47.6566923', '47.6567923', '-122.3127789', '-122.3126789'],
  'lat': '47.6567423',
  'lon': '-122.3127289',
  'display_name': '1410, Northeast Campus Parkway, West Campus, University District, Seattle, King County, Washington, 98195, United States',
  'class': 'amenity',
  'type': 'polling_station',
  'importance': 0.6300099999999998,
  'address': {'house_number': '1410',
   'road': 'Northeast Campus Parkway',
   'neighbourhood': 'West Campus',
   'suburb': 'University District',
   'city': 'Seattle',
   'county': 'King County',
   'state': 'Washington',
   'ISO3166-2-lvl4': 'US-WA',
   'postcode': '98195',
   'country': 'United States',
   'country_code': 'us'}},
 {'place_id': 20525390,
  'licence': 'Data © OpenStreetMap contributors, ODbL 1.0. https://osm.org/copyright',
  'osm_type': 'way',
  'osm_id': 54356424,
  'boundingbox': ['47.6563143', '47.6567567', '-122.3131472', '-122.3122645'],
  'lat': '47.656469799999996',
  'lon': '-122.31270835458191',
  'display_name': 'Schmitz Hall, 1410, Northeast Campus Parkway, West Campus, University District, Seattle, King County, Washington, 98195, United States',
  'class': 'building',
  'type': 'office',
  'importance': 0.6300099999999998,
  'address': {'building': 'Schmitz Hall',
   'house_number': '1410',
   'road': 'Northeast Campus Parkway',
   'neighbourhood': 'West Campus',
   'suburb': 'University District',
   'city': 'Seattle',
   'county': 'King County',
   'state': 'Washington',
   'ISO3166-2-lvl4': 'US-WA',
   'postcode': '98195',
   'country': 'United States',
   'country_code': 'us'}},
 {'place_id': 20418980,
  'licence': 'Data © OpenStreetMap contributors, ODbL 1.0. https://osm.org/copyright',
  'osm_type': 'node',
  'osm_id': 1141488380,
  'boundingbox': ['47.6566117', '47.6567117', '-122.3123383', '-122.3122383'],
  'lat': '47.6566617',
  'lon': '-122.3122883',
  'display_name': '1410, Northeast Campus Parkway, West Campus, University District, Seattle, King County, Washington, 98195, United States',
  'class': 'amenity',
  'type': 'bicycle_parking',
  'importance': 0.6300099999999998,
  'address': {'house_number': '1410',
   'road': 'Northeast Campus Parkway',
   'neighbourhood': 'West Campus',
   'suburb': 'University District',
   'city': 'Seattle',
   'county': 'King County',
   'state': 'Washington',
   'ISO3166-2-lvl4': 'US-WA',
   'postcode': '98195',
   'country': 'United States',
   'country_code': 'us'}}]
```



## Setup Reference

Docker compose pulled from:
https://github.com/mediagis/nominatim-docker/tree/master/4.4

The container setup is two parts
- The download part
- The materialization part

By default we're only downloading the North America open street map set which takes about 30 minute to download and get the container setup.

```
+ curl -L -A mediagis/nominatim-docker:4.4.0 --fail-with-body https://download.geofabrik.de/north-america-latest.osm.pbf -C - --create-dirs -o /nominatim/data.osm.pbf
  % Total    % Received % Xferd  Average Speed   Time    Time     Time  Current
                                 Dload  Upload   Total   Spent    Left  Speed
100 13.8G  100 13.8G    0     0  9736k      0  0:24:52  0:24:52 --:--:-- 10.9M
```

THIS IS AN IMPORTANT READ:
https://nominatim.org/release-docs/4.4/admin/Import/

My intial problems setting up the container was the materialization after the download: I simply didn't have enough RAM and it would crash out after a few minutes. Once I moved the container to a swarm node with 250GB of RAM, the process did end up being very 
RAM hungry while only really taking up 1 CPU core at a time.

Setup started via docker stack deploy:
```
2024-03-19 17:24:57 lovseth@swarm01:~/git_files/clad-geocoding/nominatim-docker$ docker stack deploy -c docker-compose.yml nominatim_swarm

```

Per the documentation indexing take the longest. 
>Once you see messages with Rank .. ETA appear, the indexing process has started. This part takes the most time. There are 30 ranks to process. Rank 26 and 30 are the most complex. They take each about a third of the total import time. If you have not reached rank 26 after two days of import, it is worth revisiting your system configuration as it may not be optimal for the import.

Indexing started after about 2 hours of processing:
```
 sudo -E -u nominatim nominatim import --osm-file /nominatim/data.osm.pbf --threads 24
2024-03-20 00:57:55: Using project directory: /nominatim
2024-03-20 00:57:57: Creating database
2024-03-20 00:57:57: Setting up country tables
2024-03-20 00:57:59: Importing OSM data file
2024-03-20 00:57:59  osm2pgsql version 1.11.0
2024-03-20 00:57:59  Database version: 14.11 (Ubuntu 14.11-0ubuntu0.22.04.1)
2024-03-20 00:57:59  PostGIS version: 3.2
2024-03-20 00:57:59  Storing properties to table '"public"."osm2pgsql_properties"'.
2024-03-20 02:30:10  Reading input files done in 5531s (1h 32m 11s).                      
2024-03-20 02:30:10    Processed 1895373423 nodes in 2232s (37m 12s) - 849k/s
2024-03-20 02:30:10    Processed 166919325 ways in 2936s (48m 56s) - 57k/s
2024-03-20 02:30:10    Processed 1751129 relations in 363s (6m 3s) - 5k/s
2024-03-20 02:30:10  No marked ways (Skipping stage 2).
2024-03-20 02:30:10  Clustering table 'place' by geometry...
2024-03-20 02:36:14  No indexes to create on table 'place'.
2024-03-20 02:36:14  Creating id index on table 'place'...
2024-03-20 02:37:17  Analyzing table 'place'...
2024-03-20 02:37:17  Done postprocessing on table 'planet_osm_nodes' in 0s
2024-03-20 02:37:17  Building index on table 'planet_osm_ways'
2024-03-19 19:57:22 lovseth@swarm02:~$ 

```

Once the Indexing hits, that's when all CPU's will be utilized.


Using the 'shm_size' is important for proper materialization of the database file when you adjust to bigger RAM circumstances. 
Assumes an at least 128GB RAM machine:  
```        shm_size: 64gb




## Ubuntu 'Noble' Update
Original Ubuntu Jammy vanilla install runs PHP 8.1 which has high CVE's so must be dumped.

Must update to Ubuntu 'Noble' to get php 8.3 by default. 

CVE Check on a customized build in the nominatim-php83 folder only brings up lows and mediums.
- on Ubuntu Noble
- Postgres 16 Update
- PHP 8.3 update

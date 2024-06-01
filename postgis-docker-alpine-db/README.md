# postgis-alpine
This is a single purpose container for supporting just the geocoding functions of postgis with the slimmest possible approach. Tabblock TIGER file import not needed. 

Really the postgis geocoder is just a postgres SQL query once the initialization has happened via the load_data.sh script.


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

For what's possible here see:

- https://postgis.net/docs/Geocode.html  

- https://postgis.net/docs/using_postgis_dbmanagement.html  



### Access Updates needed

Key things are:
- docker-compose - Exposing port 5432 so postgres queries can be received (example exposes it at 51005)
- update bottom of load_data.sh to customize location of querying network location pg_hba.conf


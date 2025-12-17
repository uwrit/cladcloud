#!/bin/bash

# these `sed` commands replace the DOMAIN with our local one
# and replace the year with the one we have, the actual generated 
# scripts run on the census server and on 2025

psql -d geocoder -A -t \
  -c "SELECT loader_generate_nation_script('sh');" > /gisdata/data_load.sh

sed -i 's/www2\.census\.gov/clad-github-builder.rit.uw.edu/g' /gisdata/data_load.sh
sed -i 's/2025/2020/g' /gisdata/data_load.sh
chmod +x /gisdata/data_load.sh
/gisdata/data_load.sh

psql -d geocoder -A -t \
  -c "SELECT loader_generate_script(ARRAY['FL'], 'sh');" \
  > /gisdata/data_load.sh

sed -i 's/www2\.census\.gov/clad-github-builder.rit.uw.edu/g' /gisdata/data_load.sh
sed -i 's/2025/2020/g' /gisdata/data_load.sh
chmod +x /gisdata/data_load.sh
/gisdata/data_load.sh

psql -d geocoder -A -t \
  -c "SELECT loader_generate_census_script(ARRAY['FL'], 'sh');" \
  > /gisdata/data_load.sh

sed -i 's/www2\.census\.gov/clad-github-builder.rit.uw.edu/g' /gisdata/data_load.sh
sed -i 's/2025/2020/g' /gisdata/data_load.sh
chmod +x /gisdata/data_load.sh
/gisdata/data_load.sh

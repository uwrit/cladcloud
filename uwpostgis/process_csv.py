#!/usr/bin/env python3

import pandas as pd
import os
import warnings
import psycopg
import subprocess
import sys
import time
warnings.filterwarnings('ignore')

# load states
with open('/pgdata/states', 'r') as f:
    states = f.read().split()
print(states)

# import_csv = '/opt/palantir/sidecars/shared-volumes/shared/infile.csv'
import_csv = sys.argv[1]
print("reading in " + import_csv)
# output_csv = '/opt/palantir/sidecars/shared-volumes/shared/outfile.csv'
output_csv = os.path.dirname(os.path.abspath(import_csv)) + "/outfile.csv"
print("writing to " + output_csv)

## start postgres
subprocess.Popen("postgres")
time.sleep(10)

## import infile
address_df = pd.read_csv(import_csv)

## prepare for output
address_df[['rating','stno','street',
            'styp','city','st','zip','lat','lon']] = [None, None, None, None,
                                                      None, None, None,
                                                      None, None]
address_df = address_df.reset_index(drop=True)

# setup the sql connection
# POSTGRES Connection goes here.
## destination is a Postgres database
dest_user = 'clad_svc'
dest_pw = 'not_on_gitlab'

cnxn = psycopg.connect(
    dbname='geocoder',
    user=dest_user,
    password=dest_pw,
    host='localhost',
    port=5432)

## run the loop
for address_var in range(address_df.shape[0]):
    if any(state.upper() in str(address_df.address[address_var]).upper() for state in states):
        try:
            print("processing " + str(address_df.address[address_var]))
            string_to_geocode = '''
                SELECT
                    g.rating
                , ST_AsText(ST_SnapToGrid(g.geomout,0.00001)) As wktlonlat
                , (addy).address As stno
                , (addy).streetname As street
                , (addy).streettypeabbrev As styp
                , (addy).location As city
                , (addy).stateabbrev As st
                , (addy).zip FROM geocode(''' + "'" + address_df.address[address_var] + "'" +  ''') As g;'''

            all_results = pd.read_sql(string_to_geocode, cnxn)

            # grab first result which will be one with best rating
            temp_results = all_results.head(1)
            latlong = temp_results['wktlonlat'][0].replace('POINT(','').replace(')','',).split(" ")
            print(latlong)

            address_df.rating[address_var] = temp_results.rating[0]
            address_df.stno[address_var] = temp_results.stno[0]
            address_df.street[address_var] = temp_results.street[0]
            address_df.styp[address_var] = temp_results.styp[0]
            address_df.city[address_var] = temp_results.city[0]
            address_df.st[address_var] = temp_results.st[0]
            address_df.zip[address_var] = temp_results.zip[0]
            address_df.lat[address_var] = latlong[1]
            address_df.lon[address_var] = latlong[0]

        except:
            pass

## write outout
address_df.to_csv(output_csv)
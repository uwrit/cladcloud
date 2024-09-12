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

docker run --shm-size=2g --platform linux/amd64 genoa-container-registry.washington.palantircloud.com/degauss-foundry:0.0.2


export CONTAINER_ID=0bebb78062b79630aaaeaef7b53025351663706ddee08bcd2e4327339938fe86

docker cp /Users/jtl/Desktop/uma_fips/degauss_foundry/infile2.csv $CONTAINER_ID:/opt/palantir/sidecars/shared-volumes/shared/infile.csv

touch flag_file

docker cp flag_file $CONTAINER_ID:/opt/palantir/sidecars/shared-volumes/shared/start_flag

docker cp $CONTAINER_ID:/opt/palantir/sidecars/shared-volumes/shared/outfile_geocoder_3.3.0.csv /Users/jtl/Desktop/uma_fips/degauss_foundry/outfile_test2.csv

docker cp flag_file $CONTAINER_ID:/opt/palantir/sidecars/shared-volumes/shared/close_flag

```


## Spark Sidecar Transform Setup in Foundry

Reference:
https://www.palantir.com/docs/foundry/transforms-python/transforms-sidecar/#write-a-spark-sidecar-transform

```

from transforms.api import transform, Input, Output
from transforms.sidecar import sidecar, Volume
from myproject.datasets.utils import copy_files_to_shared_directory, copy_start_flag, wait_for_done_flag
from myproject.datasets.utils import copy_output_files, copy_close_flag, launch_udf_once


@sidecar(image='degauss-foundry', tag='0.0.2', volumes=[Volume("shared")])
@transform(
    output=Output("<output dataset rid>"),
    source=Input("<input dataset rid>"),
)
def compute(output, source, ctx):
    def user_defined_function(row):
        # Copy files from source to shared directory.
        copy_files_to_shared_directory(source)
        # Send the start flag so the container knows it has all the input files
        copy_start_flag()
        # Iterate till the stop flag is written or we hit the max time limit
        wait_for_done_flag()
        # Copy out output files from the container to an output dataset
        output_fnames = [
            "start_flag",
            "outfile_geocoder_3.3.0.csv",
            "logfile",
            "done_flag",
        ]
        copy_output_files(output, output_fnames)
        # Write the close flag so the container knows you have extracted the data
        copy_close_flag()
        # The user defined function must return something
        return (row.ExecutionID, "success")
    # This spawns one task, which maps to one executor, and launches one "sidecar container"
    launch_udf_once(ctx, user_defined_function)

```

Customized Utils:

```

import os
import shutil
import time
import csv
import pyspark.sql.types as T

VOLUME_PATH = "/opt/palantir/sidecars/shared-volumes/shared"
MAX_RUN_MINUTES = 10


def write_this_row_as_a_csv_with_one_row(row):
    in_path = "/opt/palantir/sidecars/shared-volumes/shared/infile.csv"
    with open(in_path, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile, delimiter=',')
        writer.writerow(['data1', 'data2', 'data3'])
        writer.writerow([row.data1, row.data2, row.data3])


def copy_out_a_row_from_the_output_csv():
    out_path = "/opt/palantir/sidecars/shared-volumes/shared/outfile_geocoder_3.3.0.csv"
    with open(out_path, newline='') as csvfile:
        reader = csv.reader(csvfile, delimiter=',', quotechar='|')
        values = "", "", ""
        for myrow in reader:
            values = myrow[0], myrow[1], myrow[2]
        return values


def copy_output_files_with_prefix(output, output_fnames, prefix):
    for file_path in output_fnames:
        output_fs = output.filesystem()
        out_path = os.path.join(VOLUME_PATH, file_path)
        try:
            with open(out_path, "rb") as shared_file:
                with output_fs.open(f'{prefix}_{file_path}', "wb") as output_file:
                    shutil.copyfileobj(shared_file, output_file)
        except FileNotFoundError as err:
            print(err)


def copy_files_to_shared_directory(source):
    source_fs = source.filesystem()
    for item in source_fs.ls():
        file_path = item.path
        with source_fs.open(file_path, "rb") as source_file:
            dest_path = os.path.join(VOLUME_PATH, file_path)
            with open(dest_path, "wb") as shared_file:
                shutil.copyfileobj(source_file, shared_file)


def copy_start_flag():
    open(os.path.join(VOLUME_PATH, 'start_flag'), 'w')
    time.sleep(1)


def wait_for_done_flag():
    i = 0
    while i < 60 * MAX_RUN_MINUTES and not os.path.exists(os.path.join(VOLUME_PATH, 'done_flag')):
        i += 1
        time.sleep(1)


def copy_output_files(output, output_fnames):
    for file_path in output_fnames:
        output_fs = output.filesystem()
        out_path = os.path.join(VOLUME_PATH, file_path)
        try:
            with open(out_path, "rb") as shared_file:
                with output_fs.open(file_path, "wb") as output_file:
                    shutil.copyfileobj(shared_file, output_file)
        except FileNotFoundError as err:
            print(err)


def copy_close_flag():
    time.sleep(5)
    open(os.path.join(VOLUME_PATH, 'close_flag'), 'w')  # send the close flag


def launch_udf_once(ctx, user_defined_function):
    # Using a dataframe with a single row, launch user_defined_function once on that row
    schema = T.StructType([T.StructField("ExecutionID", T.IntegerType())])
    ctx.spark_session.createDataFrame([{"ExecutionID": 1}], schema=schema).rdd.foreach(user_defined_function)

```

#!/usr/bin/env python3

import argparse
import datetime
import os
import subprocess
import time

parser = argparse.ArgumentParser()
parser.add_argument("-c", "--command", type=str, help="model command to execute")
args = parser.parse_args()
the_command = args.command.split(" ")


def run_process(exe):
    "Define a function for running commands and capturing stdout line by line"
    p = subprocess.Popen(exe, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    return iter(p.stdout.readline, b"")


start_flag_fname = "/opt/palantir/sidecars/shared-volumes/shared/start_flag"
done_flag_fname = "/opt/palantir/sidecars/shared-volumes/shared/done_flag"
close_flag_fname = "/opt/palantir/sidecars/shared-volumes/shared/close_flag"

# Wait for start flag
print(f"{datetime.datetime.now(datetime.UTC).isoformat()}: waiting for start flag")
while not os.path.exists(start_flag_fname):
    time.sleep(1)
print(f"{datetime.datetime.now(datetime.UTC).isoformat()}: start flag detected")

# Execute model, logging output to file
with open("/opt/palantir/sidecars/shared-volumes/shared/logfile", "w") as logfile:
    for item in run_process(the_command):
        my_string = f"{datetime.datetime.now(datetime.UTC).isoformat()}: {item}"
        print(my_string)
        logfile.write(my_string)
        logfile.flush()
print(
    f"{datetime.datetime.now(datetime.UTC).isoformat()}: execution finished writing output file"
)

# Write out the done flag
open(done_flag_fname, "w")
print(f"{datetime.datetime.now(datetime.UTC).isoformat()}: done flag file written")

# Wait for close flag before allowing the script to finish
while not os.path.exists(close_flag_fname):
    time.sleep(1)
print(
    f"{datetime.datetime.now(datetime.UTC).isoformat()}: close flag detected. shutting down"
)

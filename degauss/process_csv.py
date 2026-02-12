#!/usr/bin/env -S uv run --script

import csv
import json
import logging
import os
import subprocess
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from typing import Any

log_format = "%(levelname)s - %(message)s"
logging.basicConfig(level=logging.INFO, format=log_format)
logger = logging.getLogger(__file__)

SHARED_DIR = Path("/opt/palantir/sidecars/shared-volumes/shared")
WORKERS = os.getenv("WORKERS", None)
if WORKERS is None:
    logger.warning("WORKERS env var not found, defaulting to 4")
    WORKERS = 4

NEW_COLS = [
    "street",
    "zip",
    "city",
    "state",
    "lat",
    "lon",
    "fips_county",
    "score",
    "prenum",
    "number",
    "precision",
]


def geocode(address: str) -> dict[str, Any] | None:
    address = address.strip()
    try:
        # NOTE: expects `geocode.rb` to be in same directory
        # as this script
        result = subprocess.run(
            ["ruby", "geocode.rb", address],
            text=True,
            check=True,
            capture_output=True,
        )
        if len(result.stdout) > 0:
            result_data = json.loads(result.stdout)
            # be explicit here, sort descending on score
            ordered_results = sorted(
                result_data,
                key=lambda x: x["score"],
                reverse=True,
            )
            best_result = ordered_results[0]
            logger.info(f"Succesfully processed: {address}")
            return best_result
        else:
            logger.info(f"Resulted in no result: {address}")
            return None
    except Exception as e:
        logger.error(f"Something went wrong: {e}")
        return None


def locate_input_file(folder: Path) -> Path:
    input_paths = sorted(folder.glob("*.csv"))
    if len(input_paths) == 0:
        raise ValueError(f"No csv file found in folder: {folder}")
    # return first path found
    return input_paths[0]


def read_csv_data(fpath: Path) -> tuple[list[str], list[dict[str, Any]]]:
    """Reads a csv and returns its column names and then the data"""
    with open(fpath, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        if "address" not in reader.fieldnames:
            logger.error("No address field found")
            raise ValueError("No address field in infile")
        data = [row for row in reader]
    return reader.fieldnames, data


def handle_row(row: dict[str, Any]) -> dict[str, Any]:
    result = geocode(address=row["address"])
    if result is None:
        logger.warning("Address had no matches, continuing...")
        return
    merged = row | result
    return merged


def main() -> None:
    logger.info("Welcome to geocode!")
    infile = locate_input_file(folder=SHARED_DIR)
    logger.info(f"Found: {infile} to process...")

    logger.info(f"Working on {infile.name}...")
    columns, data = read_csv_data(fpath=infile)
    logger.info(f"Read {len(data)} rows from csv")

    outfields = list(columns) + NEW_COLS
    outfile = SHARED_DIR / "outfile.csv"
    with open(outfile, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=outfields, lineterminator="\n")
        writer.writeheader()

        with ThreadPoolExecutor(max_workers=WORKERS) as pool:
            results = pool.map(handle_row, data)
            for row in results:
                writer.writerow(row)
                logger.debug(f"Wrote row: {row}")

    logger.info(f"Finished writing to: {outfile.name}")

    logger.info("Done")

    return


if __name__ == "__main__":
    main()

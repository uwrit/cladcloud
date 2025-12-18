# /// script
# requires-python = ">=3.14"
# dependencies = []
# ///

import csv
import json
import logging
import os
import subprocess
from pathlib import Path
from typing import Any

log_format = "%(levelname)s - %(message)s"
logging.basicConfig(level=logging.INFO, format=log_format)
logger = logging.getLogger(__file__)

SHARED_DIR = os.getenv("SHARED_DIR", None)
if SHARED_DIR is None:
    raise ValueError(
        "Expected `SHARED_DIR` env var to be present for where to look for csv files."
    )
TARGET_FOLDER = Path(SHARED_DIR)


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


def locate_file_pairs(folder: Path) -> list[tuple[Path, Path]] | None:
    input_paths = folder.glob("*.csv")
    path_pairs = []
    for input_fpath in input_paths:
        output_fpath = input_fpath.with_stem(f"{input_fpath.stem}_output")
        path_pairs.append((input_fpath, output_fpath))
    if len(path_pairs) == 0:
        logger.error(f"Found no csv files in: {folder}")
        return None
    return path_pairs


def main() -> None:
    logger.info("Welcome to geocode!")
    # parameterized so could switch if wanted
    paths = locate_file_pairs(folder=TARGET_FOLDER)
    logger.info(f"Found: {len(paths)} files to process...")

    for input_fpath, output_fpath in paths:
        logger.info(f"Working on {input_fpath.name}...")
        with (
            open(input_fpath, "r", encoding="utf-8") as infile,
            open(output_fpath, "w", encoding="utf-8") as outfile,
        ):
            reader = csv.DictReader(infile)
            if "address" not in reader.fieldnames:
                logger.error(
                    "No address field found, cannot continue with this file, moving onto next file..."
                )
                continue
            fields = list(reader.fieldnames) + NEW_COLS
            writer = csv.DictWriter(outfile, fieldnames=fields, lineterminator="\n")
            writer.writeheader()
            for row in reader:
                result = geocode(address=row["address"])
                if result is None:
                    logger.warning("Address had no matches, continuing...")
                    continue
                data = row | result
                writer.writerow(data)
                logger.debug(f"Wrote row: {data}")

        logger.info(f"Finished writing to: {outfile.name}")

    logger.info("Completed all files.")
    return


if __name__ == "__main__":
    main()

# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "psycopg2-binary",
# ]
# ///


import csv
import logging
import os
import textwrap
from pathlib import Path
from typing import Any

import psycopg2
from psycopg2.extensions import cursor as PyCursor
from psycopg2.extras import RealDictCursor

log_format = "%(levelname)s - %(message)s"
logging.basicConfig(level=logging.INFO, format=log_format)
logger = logging.getLogger(__file__)

SHARED_DIR = os.getenv("SHARED_DIR", None)
if SHARED_DIR is None:
    raise ValueError(
        "Expected `SHARED_DIR` env var to be present for where to look for csv files."
    )
TARGET_FOLDER = Path(SHARED_DIR)

PG_DB = "geocoder"
PG_USER = "postgres"
PG_PASS = "not_checked"
PG_HOST = "localhost"
PG_PORT = 5432
PG_URI = f"postgresql://{PG_USER}:{PG_PASS}@{PG_HOST}:{PG_PORT}/{PG_DB}"

NEW_COLS = [
    "rating",
    "lon",
    "lat",
    "street_no",
    "street",
    "street_type",
    "city",
    "state",
    "zip",
]

SQL = textwrap.dedent("""
SELECT 
    g.rating AS rating,
    ST_X(ST_SnapToGrid(g.geomout, 0.00001)) AS lon,
    ST_Y(ST_SnapToGrid(g.geomout, 0.00001)) AS lat,
    (addy).address AS street_no,
    (addy).streetname AS street,
    (addy).streettypeabbrev AS street_type,
    (addy).location AS city,
    (addy).stateabbrev AS state,
    (addy).zip AS zip
FROM 
    geocode(%s) AS g
ORDER BY g.rating DESC;
""")


def geocode(address: str, cursor: PyCursor) -> dict[str, Any] | None:
    address = address.strip()
    try:
        cursor.execute(SQL, [address])
        # only need 1 because first result is best match by default
        result = cursor.fetchone()
        if result is not None:
            logger.info(f"Succesfully processed: {address}")
            return result
        else:
            logger.info(f"Resulted in None: {address}")
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
            open(output_fpath, "w", encoding="utf-8", newline="") as outfile,
            psycopg2.connect(dsn=PG_URI) as conn,
        ):
            with conn.cursor(cursor_factory=RealDictCursor) as cursor:
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
                    result = geocode(address=row["address"], cursor=cursor)
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

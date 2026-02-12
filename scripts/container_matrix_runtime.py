# /// script
# requires-python = ">=3.14"
# dependencies = [
#     "geopy",
#     "polars",
#     "rich",
#     "tqdm",
# ]
# ///

import json
import logging
import shutil
import subprocess
import time
import warnings
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Literal

import polars as pl
from geopy import distance
from rich import print
from tqdm import TqdmExperimentalWarning
from tqdm.rich import tqdm

warnings.filterwarnings("ignore", category=TqdmExperimentalWarning)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    filename="data/matrix.log",
    filemode="w",
)


def load_source_df() -> pl.DataFrame:
    url = "https://raw.githubusercontent.com/brian-cy-chang/UW_Geospatial/refs/heads/main/output/OMOP_sample.csv"
    df = (
        pl.read_csv(url)
        .select(
            [
                "Location_id",
                "location_source_value",
                "latitude",
                "longitude",
                "state_abbr",
            ]
        )
        .rename(
            {
                "Location_id": "loc_id",
                "location_source_value": "address",
                "latitude": "true_lat",
                "longitude": "true_lon",
            }
        )
        .unique()
        .drop_nans()
        .drop_nulls()
        .with_columns([pl.col("state_abbr").str.to_uppercase()])
        .filter(
            # BUG: remove locations that crash current state of postgis container
            # mostly this is territories
            ~pl.col("state_abbr").is_in(("GU",))
        )
    )
    print(df)
    return df


def load_data() -> dict[str, pl.DataFrame]:
    full_df = load_source_df()
    state_map = {}
    for state_code in full_df["state_abbr"].unique().sort().to_list():
        temp = full_df.filter(pl.col("state_abbr") == state_code)
        # hard code this so we know equal size datasets
        if temp.height != 10:
            continue
        state_map[state_code] = temp
        logging.info(f"State code: {state_code} added with: {temp.height} rows")
        del temp
    return state_map


def setup_container_folder(fpath: Path) -> None:
    fpath.mkdir(exist_ok=True)
    shutil.copy(
        Path().cwd() / "flag_file",
        fpath / "start_flag",
    )
    shutil.copy(
        Path().cwd() / "flag_file",
        fpath / "close_flag",
    )
    return


def build_degauss(name: str) -> float:
    start = time.time()
    result = subprocess.run(
        [
            "docker",
            "build",
            "--platform",
            "linux/amd64",
            "-t",
            name,
            "-f",
            "Dockerfile",
            # this is the context/folder to build in which is set below with cwd
            ".",
        ],
        cwd="degauss",
        check=True,
    )
    end = time.time()
    logging.info(f"DEGAUSS CMD={' '.join(result.args)}")
    duration = end - start
    return duration


def build_postgis(name: str, state: str) -> float:
    start = time.time()
    result = subprocess.run(
        [
            "docker",
            "build",
            "--platform",
            "linux/amd64",
            "--build-arg",
            "TIGER_DOMAIN=clad-github-builder.rit.uw.edu",
            "--build-arg",
            f"state_var={state}",
            "--build-arg",
            "YEAR=2020",
            "--tag",
            name,
            "-f",
            "Dockerfile",
            # this is the context/folder to build in which is set below with cwd
            ".",
        ],
        cwd="uwpostgis",
        check=True,
    )
    logging.info(f"POSTGIS CMD={' '.join(result.args)}")
    end = time.time()
    duration = end - start
    return duration


def remove_image(name: str) -> None:
    result = subprocess.run(["docker", "image", "rm", name])
    if result.returncode != 0:
        raise ValueError(f"return code != 0: {result.returncode}")
    return


@dataclass
class Measurement:
    state: str
    container: Literal["degauss", "postgis"]
    build_time: float
    run_time: float

    def dump(self, fpath: Path) -> None:
        with open(fpath, "a") as f:
            line = json.dumps(asdict(self)) + "\n"
            f.write(line)
        return


def run_degauss(
    image_name: str,
    state: str,
) -> float:
    start = time.time()
    result = subprocess.run(
        [
            "docker",
            "run",
            "--rm",
            "--platform",
            "linux/amd64",
            "-v",
            f"{(Path().cwd() / 'data' / 'container-data').resolve()}:/opt/palantir/sidecars/shared-volumes/shared",
            image_name,
        ],
        check=True,
    )
    end = time.time()
    logging.info(f"DEGAUSS CMD={' '.join(result.args)}")

    duration = end - start
    # move output file out
    shutil.move(
        "data/container-data/outfile.csv",
        f"data/outputs/{image_name}-{state}.csv",
    )

    return duration


def run_postgis(
    image_name: str,
    state: str,
) -> float:
    start = time.time()
    result = subprocess.run(
        [
            "docker",
            "run",
            "--rm",
            "--platform",
            "linux/amd64",
            "-v",
            f"{(Path().cwd() / 'data' / 'container-data').resolve()}:/opt/palantir/sidecars/shared-volumes/shared",
            image_name,
        ],
        check=True,
    )
    end = time.time()
    logging.info(f"POSTGIS CMD={' '.join(result.args)}")

    duration = end - start
    # move output file out
    shutil.move(
        "data/container-data/outfile.csv",
        f"data/outputs/{image_name}-{state}.csv",
    )

    return duration


def trivy_check(image_name: str, fail: bool = False) -> tuple[bool, float]:
    start = time.time()
    result = subprocess.run(
        [
            "trivy",
            "image",
            "--severity=HIGH,CRITICAL",
            "--exit-code=1",
            image_name,
        ],
        check=fail,
    )
    end = time.time()
    duration = end - start
    return result.returncode == 0, duration


def docker_scout_check(image_name: str, fail: bool = False) -> tuple[bool, float]:
    start = time.time()
    result = subprocess.run(
        [
            "docker",
            "scout",
            "cves",
            "--only-severity=critical,high",
            "--exit-code",
            image_name,
        ],
        check=fail,
    )
    end = time.time()
    duration = end - start
    return result.returncode == 0, duration


def docker_scout_recs(image_name: str) -> tuple[bool, float]:
    start = time.time()
    result = subprocess.run(
        [
            "docker",
            "scout",
            "recommendations",
            image_name,
        ],
    )
    end = time.time()
    duration = end - start
    return result.returncode == 0, duration


def analyze_measurements(fpath: Path) -> pl.DataFrame:
    df = pl.read_ndjson(fpath)
    df.write_csv(Path().cwd() / "data" / "measurements.csv")
    # drop state
    rdf = df.group_by("container").agg(
        [
            pl.col("build_time").mean().alias("avg_build_time"),
            pl.col("run_time").mean().alias("avg_run_time"),
        ]
    )
    return rdf


def analyze_outputs(source_df: pl.DataFrame) -> pl.DataFrame:
    paths = (Path().cwd() / "data" / "outputs").glob("*.csv")
    results: list[dict[str, int | float | str]] = []
    none_skips = 0
    for p in paths:
        path_parts = p.stem.split("-")
        container = path_parts[0]
        state = path_parts[-1]
        data = (
            pl.read_csv(p)
            .select(["loc_id", "true_lat", "true_lon", "lat", "lon"])
            .to_dicts()
        )
        for item in data:
            id = int(item["loc_id"])
            if any(
                x is None
                for x in (item["lat"], item["lon"], item["true_lat"], item["true_lon"])
            ):
                none_skips += 1
                continue
            true_point = (float(item["true_lat"]), float(item["true_lon"]))
            coded_point = (float(item["lat"]), float(item["lon"]))
            meters_dist = distance.distance(true_point, coded_point).kilometers * 1_000
            results.append(
                {
                    "id": id,
                    "container": container,
                    "state": state,
                    "distance": meters_dist,
                }
            )

    logging.info(f"Skipped {none_skips} `None`-like types")
    df = pl.DataFrame(results)
    df.write_csv(Path().cwd() / "data" / "outputs.csv")
    rdf = df.group_by(["container", "state"]).agg(
        [pl.col("distance").mean().alias("avg_dist_meters")]
    )
    print(
        df.group_by(["container"]).agg(
            [pl.col("distance").mean().alias("avg_dist_meters")]
        )
    )
    rdf.write_csv(Path().cwd() / "data" / "outputs" / "distance_metrics.csv")
    return rdf


def main() -> None:
    logging.info("Collecting container matrix measurements")
    state_map = load_data()
    print(f"State keys: {list(state_map.keys())}")
    logging.info(f"Using: {len(state_map)} states...")

    output_path = Path().cwd() / "data" / "results.jsonl"
    with open(output_path, "w") as f:
        f.truncate()

    logging.info("Building degauss ONCE...")
    degauss_name = "degauss-global"
    degauss_build_time = build_degauss(name=degauss_name)

    logging.info("Checking degauss...")
    trivy_status, trivy_time = trivy_check(image_name=degauss_name)
    docker_scout_status, docker_scout_time = docker_scout_check(image_name=degauss_name)
    docker_scout_rec_status, docker_scout_rec_time = docker_scout_recs(
        image_name=degauss_name
    )

    i = 0
    for state, df in tqdm(state_map.items(), desc="States...", leave=False):
        i += 1
        if i > 3:
            break
        logging.info(f"====={state}=====")
        print(f"====={state}=====")

        lower_state = state.lower()
        state_fpath = Path().cwd() / "data" / f"{state}.csv"
        relative_path = state_fpath.relative_to(Path().cwd())
        logging.info(f"Dumping state datafile to: {relative_path}")
        df.write_csv(state_fpath)

        # copy file to expected name
        shutil.copy2(state_fpath, state_fpath.parent / "container-data" / "infile.csv")

        logging.info(f"Running {degauss_name} container for state={state}...")
        degauss_run_time = run_degauss(image_name=degauss_name, state=state)

        m = Measurement(
            state=state,
            container="degauss",
            build_time=degauss_build_time,
            run_time=degauss_run_time,
        )
        m.dump(fpath=output_path)
        print(m)

        postgis_name = f"postgis-{lower_state}"

        logging.info(f"Building {postgis_name} image...")
        duration = build_postgis(name=postgis_name, state=lower_state)

        logging.info("Checking postgis...")
        trivy_status, trivy_time = trivy_check(image_name=postgis_name)
        docker_scout_status, docker_scout_time = docker_scout_check(
            image_name=postgis_name
        )
        docker_scout_rec_status, docker_scout_rec_time = docker_scout_recs(
            image_name=postgis_name
        )

        postgis_run_time = run_postgis(image_name=postgis_name, state=state)

        m = Measurement(
            state=state,
            container="postgis",
            build_time=duration,
            run_time=postgis_run_time,
        )
        m.dump(fpath=output_path)
        print(m)

        logging.info(f"Removing {postgis_name} image now...")
        remove_image(name=postgis_name)

        logging.info(f"Removing state datafile from: {relative_path}")
        state_fpath.unlink()

        # clean dir data files (this is the remaining `infile.csv`)
        for f in (Path().cwd() / "data" / "container-data").glob("*.csv"):
            f.unlink()

    logging.info("Starting cleanup...")

    logging.info(f"Removing {degauss_name} image...")
    remove_image(name=degauss_name)

    logging.info("Analyzing measurements...")
    measurement_results = analyze_measurements(fpath=output_path)
    print(measurement_results)

    logging.info("Analyzing outputs...")
    output_results = analyze_outputs(source_df=load_source_df())
    print(output_results)

    logging.info("Done.")

    return


if __name__ == "__main__":
    main()

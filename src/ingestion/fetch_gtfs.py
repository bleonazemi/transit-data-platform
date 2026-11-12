"""GTFS Static Transit Feed Ingestion & Parquet Serialization.

Downloads Chicago Transit Authority (CTA) static GTFS feeds, extracts the
raw CSV/TXT tables, enforces strict Polars schemas with geographic validation,
and writes compressed columnar Parquet files for downstream DuckDB and dbt modeling.
"""

from io import BytesIO 
from pathlib import Path
import zipfile
import polars as pl 
import requests 

GTFS_FEED_URL = "https://www.transitchicago.com/downloads/sch_data/google_transit.zip"

RAW_DIR = Path("data/raw")
PROCESSED_DIR = Path("data/processed")



def download_and_extract(url: str, output_dir: Path) -> Path:
    """Download a GTFS ZIP archive into memory and extract its contents to disk.

    Args:
        url: Remote HTTP/HTTPS endpoint serving the GTFS ZIP bundle.
        output_dir: Target local directory for extracted `.txt` tables.

    Returns:
        Path to the directory containing the extracted GTFS files.

    Raises:
        requests.HTTPError: If the transit agency server returns a 4xx/5xx status.
        requests.Timeout: If the request exceeds the 30-second timeout threshold.
    """
    output_dir.mkdir(parents=True, exist_ok=True)
    print(f"Downloading transit feed from {url}...")
    response = requests.get(url, timeout=30)
    response.raise_for_status()

    with zipfile.ZipFile(BytesIO(response.content)) as zip_ref:
        zip_ref.extractall(output_dir)
    print(f"Extracted GTFS tables to {output_dir}")
    return output_dir


def transform_to_parquet(raw_dir: Path, processed_dir: Path) -> None:
    """Validate schemas, filter bad coordinates, and write GTFS tables to Parquet.

    Uses Polars lazy scanning (`scan_csv`) for large tables (`stops`, `stop_times`)
    to minimize peak memory overhead. Preserves transit identifiers as `pl.String`
    to prevent leading-zero loss or alphanumeric parsing errors, and retains GTFS
    timestamps as strings to support post-midnight schedules (e.g., '25:30:00').

    Args:
        raw_dir: Directory containing extracted GTFS `.txt` files.
        processed_dir: Output directory where `.parquet` files will be written.
    """
    processed_dir.mkdir(parents=True, exist_ok=True)

    # 1. Stops: Enfore coordinate types and filter out corruoted GPS points
    stops_df =(
        pl.scan_csv(
            raw_dir / "stops.txt",
            schema_overrides={
                "stop_id": pl.String,
                "stop_code": pl.String,
                "stop_lat": pl.Float64,
                "stop_lon": pl.Float64,
            },
        )
        .filter(
        pl.col("stop_lat").is_between(41.0, 43.0)
        & pl.col("stop_lon").is_between(-89.0, -87.0)
    )
    .collect()
    )
    stops_df.write_parquet(processed_dir / "stops.parquet")
    print(f"Wrote stops.parquet ({stops_df.height:,}rows)")
    
    # 2. Routes: Retain route_id as String for alphanumeric rail/express lines
    routes_df = pl.read_csv(
        raw_dir / "routes.txt",
        schema_overrides={
            "route_id": pl.String,
            "route_short_name": pl.String,
            "route_long_name": pl.String,
            "route_type": pl.Int32,
        },
    )
    routes_df.write_parquet(processed_dir / "routes.parquet")
    print(f"Wrote routes.parquet ({routes_df.height:,} rows)")

    # 3. Trips: Link routes, service calenders, and route shapes
    trips_df = pl.read_csv(
        raw_dir / "trips.txt",
        schema_overrides={
            "route_id": pl.String,
            "service_id": pl.String,
            "trip_id": pl.String,
            "shape_id": pl.String,
            "direction_id": pl.Int32,
        },
    )
    trips_df.write_parquet(processed_dir / "trips.parquet")
    print(f"Wrote trips.parquet ({trips_df.height:,} rows)")

    # 4. Stop Times: Stream via lazy scan to handle multi-million-row schedules
    stop_times_df = (
        pl.scan_csv(
            raw_dir / "stop_times.txt",
            schema_overrides={
                "trip_id": pl.String,
                "stop_id": pl.String,
                "stop_sequence": pl.Int32,
                "arrival_time": pl.String,
                "departure_time": pl.String,
            },
        )
        .filter(pl.col("stop_sequence") >= 0)
        .collect()
    )
    stop_times_df.write_parquet(processed_dir / "stop_times.parquet")
    print(f"Wrote stop_times.parquet ({stop_times_df.height:,} rows)")


if __name__ == "__main__":
    download_and_extract(GTFS_FEED_URL, RAW_DIR)
    transform_to_parquet(RAW_DIR, PROCESSED_DIR)
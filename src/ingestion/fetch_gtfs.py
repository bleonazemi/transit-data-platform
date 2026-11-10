from io import BytesIO ## Letting pyton treat the raw downloaded btes stored in RAM as if it were an open file on disk
from pathlib import Path
import zipfile
import polars as pl 
import requests ## HTTP library used to send GET requests to fetch data from APIs and web servers

GTFS_FEED_URL = "https://www.transitchicago.com/downloads/sch_data/google_transit.zip"

RAW_DIR = Path("data/raw")
PROCESSED_DIR = Path("data/processed")

## RAW_DIR points to the local file full of raw unzipped CSVs
## PROCESSED_DIR points to the "clean" folder where all the cleaned and optimized data will be stored


def download_and_extract(url: str, output_dir: Path) -> Path:
    output_dir.mkdir(parents=True, exist_ok=True)
    print(f"Downloading transit feed from {url}...")
    response = requests.get(url, timeout=30)
    response.raise_for_status()

    with zipfile.ZipFIle(BytesIO(response.content)) as zip_ref:
        zip_ref.extractall(output_dir)
    print(f"Extracted GTFS tables to {output_dir}")
    return output_dir

## download_and_extract is a func that takes a URL Path and target dir and returns the output dir Path 
    ## - creating any dirs along the way if none exist using parents=True and prevents python from throwing an error a dir already exists using exists_ok=True
    ## - requests.get sends a GET request to download ZIP boundles using time=30 as defensive programming tactic in the event the transit agency stops requesting preventing indefinite wait times
    ## - along the way response.raise_for_status() checks the HTTP server for returing errors raising an exception and stops execution  
    ## - finally zipfile.ZipFIle(BytesIO(response.content)) opens raw response bytes inside memory via BytesIO interpreting them as ZIP archive and extracts all text files into raw/data and logs the conformation to stdout and returns the path 

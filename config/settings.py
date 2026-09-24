import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()
BASE = Path(__file__).resolve().parent.parent
RAW_FILE = BASE / "data" / "raw" / "online_retail_II.csv"
CLEAN_DIR = BASE / "data" / "clean"
REJECT_DIR = BASE / "data" / "rejected"

DB = dict(
    host=os.getenv("POSTGRES_HOST", "localhost"),
    port=os.getenv("POSTGRES_PORT", "5432"),
    dbname=os.getenv("POSTGRES_DB"),
    user=os.getenv("POSTGRES_USER"),
    password=os.getenv("POSTGRES_PASSWORD"),
)
S3_BUCKET = os.getenv("S3_BUCKET")

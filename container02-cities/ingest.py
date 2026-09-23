"""Extrae el 100% de las tablas de MS2 y las carga en S3 como CSV."""
import os
from datetime import datetime
from pathlib import Path
import boto3
import pandas as pd
import psycopg2
from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parents[1] / ".env")
stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
connection = psycopg2.connect(host=os.getenv("CITIES_DB_HOST", "127.0.0.1"), port=int(os.getenv("CITIES_DB_PORT", "5432")), dbname=os.getenv("CITIES_DB_NAME", "db2_urban_exposure"), user=os.getenv("CITIES_DB_USER", "postgres"), password=os.getenv("CITIES_DB_PASSWORD", ""), connect_timeout=5)
s3 = boto3.client("s3", region_name=os.getenv("AWS_REGION", "us-east-1"))
bucket = os.environ["S3_BUCKET"]
prefix = os.getenv("S3_PREFIX", "").strip("/")
files = []
try:
    for table in ("cities", "sensitive_sites"):
        filename = Path(f"{table}_{stamp}.csv")
        pd.read_sql_query(f"SELECT * FROM {table}", connection).to_csv(filename, index=False)
        key = f"{prefix}/ms2/{table}/{filename.name}" if prefix else f"ms2/{table}/{filename.name}"
        s3.upload_file(str(filename), bucket, key)
        files.append(filename)
        print(f"MS2: {table} exportada y cargada en s3://{bucket}/{key}")
finally:
    connection.close()
    for filename in files:
        filename.unlink(missing_ok=True)

"""Extrae el 100% de las tablas de MS1 y las carga en S3 como CSV."""
import os
from datetime import datetime
from pathlib import Path
import boto3
import mysql.connector
import pandas as pd
from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parents[1] / ".env")
stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
connection = mysql.connector.connect(host=os.getenv("FIRE_DB_HOST", "127.0.0.1"), port=int(os.getenv("FIRE_DB_PORT", "3306")), user=os.getenv("FIRE_DB_USER", "root"), password=os.getenv("FIRE_DB_PASSWORD", ""), database=os.getenv("FIRE_DB_NAME", "db1_fire_catalog"), connect_timeout=5)
s3 = boto3.client("s3", region_name=os.getenv("AWS_REGION", "us-east-1"))
bucket = os.environ["S3_BUCKET"]
prefix = os.getenv("S3_PREFIX", "").strip("/")
files = []
try:
    for table in ("fire_events", "fire_detections"):
        filename = Path(f"{table}_{stamp}.csv")
        pd.read_sql_query(f"SELECT * FROM {table}", connection).to_csv(filename, index=False)
        key = f"{prefix}/ms1/{table}/{filename.name}" if prefix else f"ms1/{table}/{filename.name}"
        s3.upload_file(str(filename), bucket, key)
        files.append(filename)
        print(f"MS1: {table} exportada y cargada en s3://{bucket}/{key}")
finally:
    connection.close()
    for filename in files:
        filename.unlink(missing_ok=True)

import mysql.conector
import pandas as pd
import boto3
from datetime import datetime

conn = mysql.connector.connect(
    host="HOST_DE_LA_VM_DE_BASES_DE_DATOS",
    user="root",
    password="smokecast123",
    database="fire_catalog",
)

df = pd.read_sql("SELECT * FROM fire_detections", conn)

filename = f"fire_detections_{datetime.now().strftime('%Y%m%d_%H%M')}.csv"
df.to_csv(filename, index=False)
print(f"Generado {filename} con {len(df)} filas")


s3 = boto3.client("s3", region_name="us-east-1")
s3.upload_file(filename, "smokecast-datalake", f"fires/{filename}")
print("Subido a S3 correctamente")
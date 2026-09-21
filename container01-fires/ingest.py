import mysql.connector 
import pandas as pd
import boto3 
from datetime import datetime
import os
from dotenv import load_dotenv

# Cargar las variables de entorno
load_dotenv()

filename = f"fire_detections_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
conn = None

try:
    
    #Configuración de base de datos MySQL
    print(f"Conectando a MySQL en {os.getenv('DB_HOST', 'localhost')}...")
    conn = mysql.connector.connect(
        host=os.getenv("DB_HOST", "localhost"),
        user=os.getenv("DB_USER", "root"),
        password=os.getenv("DB_PASSWORD"),
        database=os.getenv("DB_NAME", "fire_catalog"),
        connect_timeout=5
    )
    df = pd.read_sql("SELECT * FROM fire_detections", conn)
    df.to_csv(filename, index=False)
    print(f"Archivo local generado: {filename} ({len(df):,} filas extraidas)")
    
    s3_bucket = os.getenv("S3_BUCKET", "smokecast-datalake")
    print(f"Subiendo {filename} a s3://{s3_bucket}/fires/...")
    s3 = boto3.client("s3", region_name=os.getenv("AWS_REGION", "us-east-1"))
    s3.upload_file(filename, s3_bucket, f"fires/{filename}")
    print("Subido a S3 correctamente.")

except Exception as e:
    print(f"Error: {e}")
    raise e
finally:
    if conn:
        conn.close()
    if os.path.exists(filename):
        os.remove(filename)

import os
from datetime import datetime
import pandas as pd
from pymongo import MongoClient
import boto3
from dotenv import load_dotenv
from pathlib import Path

# Cargar las variables de entorno
load_dotenv(Path(__file__).resolve().parents[1] / ".env")

filename = f"weather_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jsonl"
client = None

try:
    mongo_host = os.getenv("WEATHER_MONGO_HOST", "127.0.0.1")
    mongo_port = int(os.getenv("WEATHER_MONGO_PORT", 27017))
    mongo_user = os.getenv("WEATHER_MONGO_USER", "")
    mongo_pass = os.getenv("WEATHER_MONGO_PASSWORD", "")

    print(f"Conectando a MongoDB en {mongo_host}:{mongo_port}...")
    # URI de conexión protegida con usuario y contraseña
    mongo_options = {"serverSelectionTimeoutMS": 5000}
    if bool(mongo_user) != bool(mongo_pass):
        raise ValueError("WEATHER_MONGO_USER y WEATHER_MONGO_PASSWORD deben configurarse juntos")
    if mongo_user:
        mongo_options.update(username=mongo_user, password=mongo_pass,
                             authSource=os.getenv("MONGO_AUTH_SOURCE", "admin"))
    client = MongoClient(host=mongo_host, port=mongo_port, **mongo_options)

    collection = client[os.getenv("WEATHER_MONGO_DB", "db3_atmosphere_feed")][os.getenv("WEATHER_MONGO_COLLECTION", "weather_readings")]

    docs = list(collection.find({}, {"_id": 0}))
    print(f"Se extrajeron {len(docs):,} documentos de la coleccion MongoDB.")
    
    if not docs:
        print("Alerta: No hay documentos para exportar. Fin del proceso.")
        exit(0)

    df = pd.DataFrame(docs)
    df.to_json(filename, orient="records", lines=True)
    print(f"Archivo local JSON Lines generado: {filename}")

    s3_bucket = os.getenv("S3_BUCKET", "smokecast-datalake")
    prefix = os.getenv("S3_PREFIX", "").strip("/")
    s3_key = f"{prefix}/ms3/weather_readings/{filename}" if prefix else f"ms3/weather_readings/{filename}"
    print(f"Subiendo {filename} a s3://{s3_bucket}/{s3_key}...")
    s3 = boto3.client("s3", region_name=os.getenv("AWS_REGION", "us-east-1"))
    s3.upload_file(filename, s3_bucket, s3_key)
    print("Subido a S3 correctamente.")

except Exception as e:
    print(f"Error: {e}")
    raise e
finally:
    if client:
        client.close()
    if os.path.exists(filename):
        os.remove(filename)

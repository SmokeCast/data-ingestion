import os
from datetime import datetime
import pandas as pd
from pymongo import MongoClient
import boto3
from dotenv import load_dotenv

# Cargar las variables de entorno
load_dotenv()

filename = f"weather_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
client = None

try:
    mongo_host = os.getenv("MONGO_HOST", "localhost")
    mongo_port = int(os.getenv("MONGO_PORT", 27017))
    mongo_user = os.getenv("MONGO_USER", "root")
    mongo_pass = os.getenv("MONGO_PASSWORD", "password")

    print(f"Conectando a MongoDB en {mongo_host}:{mongo_port}...")
    # URI de conexión protegida con usuario y contraseña
    client = MongoClient(
        host=mongo_host,
        port=mongo_port,
        username=mongo_user,
        password=mongo_pass,
        authSource="admin",
        serverSelectionTimeoutMS=5000
    )

    collection = client[os.getenv("MONGO_DB", "atmosphere_feed")][os.getenv("MONGO_COLLECTION", "weather_readings")]

    docs = list(collection.find({}, {"_id": 0}))
    print(f"Se extrajeron {len(docs):,} documentos de la coleccion MongoDB.")
    
    if not docs:
        print("Alerta: No hay documentos para exportar. Fin del proceso.")
        exit(0)

    df = pd.DataFrame(docs)
    df.to_json(filename, orient="records", lines=True)
    print(f"Archivo local JSON Lines generado: {filename}")

    s3_bucket = os.getenv("S3_BUCKET", "smokecast-datalake")
    print(f"Subiendo {filename} a s3://{s3_bucket}/weather/...")
    s3 = boto3.client("s3", region_name=os.getenv("AWS_REGION", "us-east-1"))
    s3.upload_file(filename, s3_bucket, f"weather/{filename}")
    print("Subido a S3 correctamente.")

except Exception as e:
    print(f"Error: {e}")
    raise e
finally:
    if client:
        client.close()
    if os.path.exists(filename):
        os.remove(filename)
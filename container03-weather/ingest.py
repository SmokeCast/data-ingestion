import os
from datetime import datetime
import pandas as pd
from pymongo import MongoClient

# Configuración dinámica
MONGO_HOST = os.getenv("MONGO_HOST", "localhost")
MONGO_PORT = int(os.getenv("MONGO_PORT", 27017))
MONGO_DB = os.getenv("MONGO_DB", "atmosphere_feed")
MONGO_COLLECTION = os.getenv("MONGO_COLLECTION", "weather_readings")
S3_BUCKET = os.getenv("S3_BUCKET", "smokecast-datalake")
AWS_REGION = os.getenv("AWS_REGION", "us-east-1")

print(f"[Ingesta Ms3] Conectando a MongoDB en {MONGO_HOST}:{MONGO_PORT}...")
client = MongoClient(host=MONGO_HOST, port=MONGO_PORT, serverSelectionTimeoutMS=5000)
collection = client[MONGO_DB][MONGO_COLLECTION]

docs = list(collection.find({}, {"_id": 0}))
print(f"[Ingesta Ms3] Se extrajeron {len(docs):,} documentos de la coleccion '{MONGO_COLLECTION}'.")

if not docs:
    print("[Ingesta Ms3] Alerta: No hay documentos para exportar. Fin del proceso.")
    exit(0)

df = pd.DataFrame(docs)

timestamp_str = datetime.now().strftime("%Y%m%d_%H%M")
filename = f"weather_{timestamp_str}.json"

# Exportar en formato JSON Lines (records) para optimizar consultas de Data Science / Athena
df.to_json(filename, orient="records", lines=True)
print(f"[Ingesta Ms3] Archivo local generado exitosamente: {filename} ({len(df):,} filas)")

# Subida a AWS S3
try:
    import boto3
    s3 = boto3.client("s3", region_name=AWS_REGION)
    s3_key = f"weather/{filename}"
    print(f"[Ingesta Ms3] Subiendo {filename} a s3://{S3_BUCKET}/{s3_key}...")
    s3.upload_file(filename, S3_BUCKET, s3_key)
    print(f"[Ingesta Ms3] Subido exitosamente a S3: s3://{S3_BUCKET}/{s3_key}")
except Exception as e:
    print(f"[Ingesta Ms3] Aviso S3: {e}")
    print("  --> El archivo JSON quedo generado localmente y listo para subirse cuando las credenciales de AWS esten activas.")

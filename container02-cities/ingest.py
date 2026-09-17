import psycopg2
import pandas as pd
#import boto3
from datetime import datetime

conn = psycopg2.connect(
    host="localhost",  # cambiar más adelante cuando la base esté en la VM de AWS
    dbname="urban_exposure",
    user="postgres",
    password="smokecast123"
)
df = pd.read_sql("SELECT * FROM cities", conn)

filename = f"cities_{datetime.now().strftime('%Y%m%d_%H%M')}.csv"
df.to_csv(filename, index=False)
print(f"Generado {filename} con {len(df)} filas")

# s3 = boto3.client('s3', region_name='us-east-1')
# s3.upload_file(filename, 'smokecast-datalake', f'cities/{filename}')
# print("Subido a S3 correctamente")
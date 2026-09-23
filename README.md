# Ingesta a S3

Cada script extrae el 100 % de las tablas de su microservicio y genera un archivo
por tabla antes de cargarlo en S3:

- `container01-fires`: `fire_events` y `fire_detections` desde MySQL.
- `container02-cities`: `cities` y `sensitive_sites` desde PostgreSQL.
- `container03-weather`: `weather_readings` desde MongoDB en JSON Lines.

Los nombres, columnas y tipos canónicos para Glue/Athena están en
[`athena_schema.json`](./athena_schema.json). Se basan en las tablas reales de
MS1, MS2 y MS3; no agregan columnas como `seed_id` a las tablas SQL.

El JSON es una referencia y no crea recursos de AWS por sí solo. Para crear la
infraestructura de la MV de ingesta, el bucket S3, `smokecast_analytics` y las
cinco tablas de Glue usa la plantilla
`iac_containers_and_scripting/iac_cloudformation/iac_crear_smokecast_ingesta.yml`.
La plantilla usa CSV para MS1/MS2 y JSON Lines para MS3:

```bash
aws cloudformation deploy \
  --template-file iac_containers_and_scripting/iac_cloudformation/iac_crear_smokecast_ingesta.yml \
  --stack-name smokecast-ingesta \
  --parameter-overrides BucketName=smokecast-datalake
```

Si las columnas no cambian, las siguientes ingestas solo agregan archivos y no
requieren recrear las tablas.

Desde esta carpeta instala las dependencias con `pip install -r requirements.txt`
si vas a ejecutar los scripts directamente. Para Docker, el Compose de
despliegue está en
`iac_containers_and_scripting/containers-and-seeds/mv_ingesta/`.
Las claves se escriben directamente bajo `ms1/`, `ms2/` y `ms3/` dentro del
bucket configurado. S3 crea esos prefijos automáticamente al subir el primer
objeto.
Los archivos temporales se eliminan después de cargarse correctamente.

## Ejecución en la MV de ingesta

La extracción utiliza estrategia **pull**: cada contenedor abre una conexión de
solo lectura, ejecuta `SELECT *` en las bases SQL o `find({})` en MongoDB,
exporta el 100 % de los registros y termina. No depende de webhooks ni de
procesamiento incremental.

Para ejecutarla con Docker Compose:

```bash
cd iac_containers_and_scripting/containers-and-seeds/mv_ingesta
cp env.example .env
# Configura FIRE_DB_HOST, CITIES_DB_HOST y WEATHER_MONGO_HOST.
docker compose pull
docker compose run --rm fires-ingestion
docker compose run --rm cities-ingestion
docker compose run --rm weather-ingestion
```

Los servicios tienen `restart: "no"` porque cada ejecución es un job puntual:
extrae, sube los archivos y termina. Compose no actúa como planificador.

## Ejecución periódica con cron

En la MV de ingesta se puede programar el Compose con el cron del sistema. Por
ejemplo, si el proyecto está instalado en `/opt/smokecast/mv_ingesta`, crea un
script ejecutable `/usr/local/bin/smokecast-ingesta.sh`:

```bash
#!/usr/bin/env bash
set -euo pipefail
cd /opt/smokecast/mv_ingesta
flock -n /var/run/smokecast-ingesta.lock bash -c '
  docker compose --env-file .env run --rm fires-ingestion &&
  docker compose --env-file .env run --rm cities-ingestion &&
  docker compose --env-file .env run --rm weather-ingestion
'
```

Después registra, por ejemplo, una ejecución diaria a las 02:00:

```cron
0 2 * * * /usr/local/bin/smokecast-ingesta.sh >> /var/log/smokecast-ingesta.log 2>&1
```

`flock` evita que una ejecución nueva empiece mientras la anterior sigue
leyendo o subiendo datos. Para otra frecuencia cambia la expresión de cron.
También se puede usar un timer de systemd, pero no es necesario para esta
arquitectura.

Cada ejecución crea objetos nuevos con marca temporal bajo `ms1/`, `ms2/` y
`ms3/`; no elimina los archivos anteriores. Esto permite conservar el histórico
para Athena. Si se desea retener solamente una ventana de tiempo, configura
una regla de ciclo de vida del bucket S3.

FROM python:3.11-slim
WORKDIR /app
COPY ingest.py .
RUN pip install --no-cache-dir pandas boto3 python-dotenv psycopg2-binary
CMD [ "python", "ingest.py" ]
FROM python:3.11-slim
WORKDIR /app
COPY ingest.py .
RUN pip install psycopg2-binary pandas boto3
CMD ["python", "ingest.py"]
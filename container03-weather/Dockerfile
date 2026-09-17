FROM python:3.11-slim
WORKDIR /app
COPY ingest.py .
RUN pip install --no-cache-dir pymongo pandas boto3
CMD ["python", "ingest.py"]

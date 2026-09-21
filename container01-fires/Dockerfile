FROM python:3.11-slim
WORKDIR /app
COPY ingest.py .
RUN pip install --no-cache-dir pandas boto3 python-dotenv mysql-connector-python
CMD [ "python", "ingest.py" ]
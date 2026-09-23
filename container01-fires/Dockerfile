FROM python:3.11-slim
WORKDIR /app
COPY ingest.py .
RUN pip install --no-cache-dir \
    pandas==2.3.3 boto3==1.40.30 python-dotenv==1.2.3 \
    mysql-connector-python==9.4.0
CMD [ "python", "ingest.py" ]

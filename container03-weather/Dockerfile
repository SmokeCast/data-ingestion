FROM python:3.11-slim
WORKDIR /app
COPY ingest.py .
RUN pip install --no-cache-dir \
    pandas==2.3.3 boto3==1.40.30 python-dotenv==1.2.3 \
    pymongo==4.18.1
CMD [ "python", "ingest.py" ]

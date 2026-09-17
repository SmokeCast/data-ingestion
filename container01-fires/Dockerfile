FROM python:3.11-slim
WORKDIR /app
COPY ingest.py .
RUN pip install mysql-connector-python pandas boto3
CMD [ "python", "ingest.py" ]
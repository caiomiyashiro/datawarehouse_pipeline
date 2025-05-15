FROM apache/airflow:2.10.5-python3.11
COPY requirements.txt /
RUN pip install --no-cache-dir -r /requirements.txt
# RUN pip install apache-airflow-providers-docker pyarrow azure-storage-file-datalake
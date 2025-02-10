from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.providers.postgres.hooks.postgres import PostgresHook
from airflow.providers.microsoft.azure.hooks.data_lake import AzureDataLakeStorageV2Hook
from datetime import datetime, timedelta
import pyarrow as pa
import pyarrow.parquet as pq
import io
from collections import defaultdict
import logging

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime(2024, 8, 1),
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

dag = DAG(
    'fact_sales',
    default_args=default_args,
    description='Extract data from PostgreSQL and store in Data Lake as Parquet in a single step',
    schedule_interval='@daily',
    catchup=False,
)

def extract_and_load_data(prev_ds=None, **kwargs):
    if prev_ds is None:
        prev_ds = kwargs.get('prev_ds', (datetime.now() - timedelta(days=-1)).strftime('%Y-%m-%d'))
    
    logging.info(f"Processing data for date: {prev_ds}")

    # Connect to PostgreSQL
    pg_hook = PostgresHook(postgres_conn_id='azure_prod_db')
    
    # Execute SQL query using the execution date
    sql = f"SELECT * FROM sales WHERE DATE(InvoiceDate) = '{prev_ds}'"
    connection = pg_hook.get_conn()
    cursor = connection.cursor()
    cursor.execute(sql)
    
    # Fetch data and column names
    columns = [desc[0] for desc in cursor.description]
    rows = cursor.fetchall()
    logging.info(f"Number of retrieved rows for {prev_ds}: {len(rows)}")
    
    # Close cursor and connection
    cursor.close()
    connection.close()
    
    if not rows:
        logging.info(f"No data found for {prev_ds}. Skipping upload.")
        return

    # Process and store data
    year, month, day = prev_ds.split('-')
    partition_path = f'raw/sales/year={year}/month={month}/{day}.parquet'   
    # Convert data to PyArrow Table
    arrays = [pa.array([row[i] for row in rows]) for i in range(len(columns))]
    table = pa.Table.from_arrays(arrays, names=columns)    
    # Convert to Parquet
    parquet_buffer = io.BytesIO()
    pq.write_table(table, parquet_buffer)

    # check if parquet data is written
    # parquet_buffer.seek(0)
    # # Read the parquet buffer
    # table = pq.read_table(parquet_buffer)   
    # logging.info(f"!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!! Parquet table: {table}")
    
    # Connect to Azure Data Lake
    adl_hook = AzureDataLakeStorageV2Hook(adls_conn_id='azure_datalake')
    # Get a reference to the file system (container)
    file_system_client = adl_hook.service_client.get_file_system_client(file_system="datalake")

    # list files in datalake
    # path_list = file_system_client.get_paths()
    # for path in path_list:
    #     logging.info(path.name + '\n')

    # Upload to Data Lake
    file_client = file_system_client.get_file_client(partition_path)
    parquet_buffer.seek(0)
    file_client.upload_data(parquet_buffer, overwrite=True)

    logging.info(f"File uploaded to {partition_path}")

extract_and_load_task = PythonOperator(
    task_id='extract_and_load_data',
    python_callable=extract_and_load_data,
    provide_context=True,
    dag=dag,
)

extract_and_load_task
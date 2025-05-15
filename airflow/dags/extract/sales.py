from airflow import DAG
from airflow.operators.python import PythonOperator, ShortCircuitOperator
from airflow.providers.common.sql.operators.sql import SQLExecuteQueryOperator

from datetime import datetime, timedelta
import sys
import os
import json
import jsonschema

sys.path.append('/opt/python')
from extract.extract_raw_sales_simulated import check_if_data_exists, generate_daily_data, validate_sales_data

default_args = {
    'owner': os.environ.get("AIRFLOW_DEFAULT_OWNER"),
    'start_date': datetime.strptime(os.environ.get("AIRFLOW_DEFAULT_START_DATE"), '%Y-%m-%d'),
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
    'catchup':True
}

conn_params={
            'dbname': os.environ.get("POSTGRES_DATA_DB"),
            'user': os.environ.get("POSTGRES_USER"),
            'password': os.environ.get("POSTGRES_PASSWORD"),
            'host': os.environ.get("POSTGRES_HOST"),  # Docker service name
            'port': os.environ.get("POSTGRES_PORT")
        }

with DAG('extract_sales', 
         default_args=default_args,
         schedule_interval='@daily',
         catchup=True,
         template_searchpath='/opt/sql/extract') as dag:

    # Check if data already exists for the given date
    # This task will skip the downstream tasks if data already exists
    check_data_exist = ShortCircuitOperator(
        task_id="check_if_data_exists",
        python_callable=check_if_data_exists,
        op_kwargs={'target_date': '{{ ds }}',
                   'conn_params': conn_params,
                   'table_name': 'sales'}
    )

    # only made to simulate prod data generation. In POC, data is stored in a CSV file but in prod, it should be stored in a temp table
    generate_daily_data = PythonOperator(
        task_id='generate_daily_data_raw_sales',
        python_callable=generate_daily_data,
        op_kwargs={'sample_data_filename': 'Online_Retail_cleaned.csv', 
                   'target_date': '{{ ds }}',
                   'conn_params': conn_params,
                   'table_name': 'sales'}
    )

    # Validate 'imported' data against data contract before inserting into raw
    # This task will raise an error if the data does not match the schema
    validate_sales_data = ShortCircuitOperator(
        task_id='validate_sales_data',
        python_callable=validate_sales_data,
        op_kwargs={
            'table_name':'sales',
            'target_date': '{{ ds }}',
            'sales_contract_filename': 'extract_sales_contract.json',
            'conn_params': conn_params
        }
    )
    
    insert_sales = SQLExecuteQueryOperator(
        task_id='insert_sales',
        conn_id='postgres_default',
        sql='extract_sales.sql'
    )

    check_data_exist >> generate_daily_data >> validate_sales_data >> insert_sales


from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.providers.common.sql.operators.sql import SQLExecuteQueryOperator

from datetime import datetime, timedelta
import sys
import pandas as pd

def generate_daily_data(target_date, **kwargs):
    """Main processing function"""
    sys.path.append('/opt/python')
    from extract.extract_raw_sales_simulated import insert_sampled_data
    
    insert_sampled_data(
        sample_data_filename='Online_Retail_cleaned.csv',
        target_date=target_date,
        conn_params={
            'dbname': 'postgres',
            'user': 'airflow',
            'password': 'airflow',
            'host': 'postgres',  # Docker service name
            'port': 5432
        }
    )

default_args = {
    'owner': 'airflow',
    'start_date': datetime(2025, 4, 1),
    'retries': 1,
    'retry_delay': timedelta(minutes=5)
}

with DAG('extract_sales', 
         default_args=default_args,
         schedule_interval='@daily',
         catchup=True) as dag:

    # only made to simulate prod data generation
    extract_raw_sales = PythonOperator(
        task_id='generate_daily_data_raw_sales',
        python_callable=generate_daily_data,
        op_kwargs={'target_date': '{{ ds }}'}
    )

    extract_raw_sales

# Note: The `PostgresOperator` requires the SQL file to be in the same directory as the DAG or provide a full path.


from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.providers.common.sql.operators.sql import SQLExecuteQueryOperator

from datetime import datetime, timedelta
import sys
import os

def generate_daily_data(target_date, **kwargs):
    """Main processing function"""
    sys.path.append('/opt/python')
    from extract.extract_raw_sales_simulated import insert_sampled_data
    
    insert_sampled_data(
        sample_data_filename='Online_Retail_cleaned.csv',
        target_date=target_date,
        conn_params={
            'dbname': os.environ.get("POSTGRES_DATA_DB"),
            'user': os.environ.get("POSTGRES_USER"),
            'password': os.environ.get("POSTGRES_PASSWORD"),
            'host': os.environ.get("POSTGRES_HOST"),  # Docker service name
            'port': os.environ.get("POSTGRES_PORT")
        }
    )

default_args = {
    'owner': os.environ.get("AIRFLOW_DEFAULT_OWNER"),
    'start_date': datetime.strptime(os.environ.get("AIRFLOW_DEFAULT_START_DATE"), '%Y-%m-%d'),
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


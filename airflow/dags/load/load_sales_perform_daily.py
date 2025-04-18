from airflow import DAG
from airflow.providers.common.sql.operators.sql import SQLExecuteQueryOperator

from datetime import datetime, timedelta
import sys
import pandas as pd

default_args = {
    'owner': 'airflow',
    'start_date': datetime(2025, 4, 1),
    'retries': 1,
    'retry_delay': timedelta(minutes=5)
}

with DAG('calculate_sales_performance', 
         default_args=default_args,
         schedule_interval='@daily',
         catchup=True,
         template_searchpath='/opt/airflow/sql/transform') as dag:

    calculate_sales_performance_daily = SQLExecuteQueryOperator(
        task_id='calculate_sales_performance_daily',
        conn_id='postgres_default',
        sql='sales_perform_daily.sql'
    )
    calculate_sales_performance_daily
# Note: The `PostgresOperator` requires the SQL file to be in the same directory as the DAG or provide a full path.


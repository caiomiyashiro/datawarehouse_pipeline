from airflow import DAG
from airflow.providers.common.sql.operators.sql import SQLExecuteQueryOperator
from airflow.sensors.external_task import ExternalTaskSensor

from datetime import datetime, timedelta

default_args = {
    'owner': 'airflow',
    'start_date': datetime(2025, 4, 15),
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
    'depends_on_past': True,
    'catchup': True
}

with DAG('transform_sales', 
         default_args=default_args,
         schedule_interval='@daily',
         template_searchpath='/opt/sql/transform') as dag:
    
    wait_for_upstream = ExternalTaskSensor(
        task_id="wait_for_load_raw_sales",
        external_dag_id="extract_sales",                    # The DAG to monitor
        external_task_id="generate_daily_data_raw_sales",   # The specific task to wait for
        allowed_states=['success'],         # Wait for success (default)
        failed_states=['failed', 'skipped'],# Fail if upstream fails/skips
        poke_interval=15,                   # Check every 15 seconds
        timeout=60*60*6,                    # Timeout after 6 hours
        mode='poke',                        # 'poke' or 'reschedule'
    )

    transform_sales = SQLExecuteQueryOperator(
        task_id='transform_sales',
        conn_id='postgres_default',
        sql='transform_sales.sql'
    )

    wait_for_upstream >> transform_sales


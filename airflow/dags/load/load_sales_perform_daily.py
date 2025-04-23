from airflow import DAG
from airflow.providers.common.sql.operators.sql import SQLExecuteQueryOperator
from airflow.sensors.external_task import ExternalTaskSensor

from datetime import datetime, timedelta
import os
import pandas as pd

default_args = {
    'owner': os.environ.get("AIRFLOW_DEFAULT_OWNER"),
    'start_date': datetime.strptime(os.environ.get("AIRFLOW_DEFAULT_START_DATE"), '%Y-%m-%d'),
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
    'catchup': True
}

with DAG('calculate_sales_performance', 
         default_args=default_args,
         schedule_interval='@daily',
         template_searchpath='/opt/sql/load') as dag:
    
    wait_for_upstream = ExternalTaskSensor(
        task_id="wait_for_dw_sales",
        external_dag_id="load_dw_tables_from_sales",    # The DAG to monitor
        external_task_id="load_fact_sales",             # The specific task to wait for
        allowed_states=['success'],                     # Wait for success (default)
        failed_states=['failed', 'skipped'],            # Fail if upstream fails/skips
        poke_interval=15,                               # Check every 15 seconds
        timeout=60*60*6,                                # Timeout after 6 hours
        mode='poke',                                    # 'poke' or 'reschedule'
    )

    calculate_sales_performance_daily = SQLExecuteQueryOperator(
        task_id='calculate_sales_performance_daily',
        conn_id='postgres_default',
        sql='load_sales_perform_daily.sql'
    )
    wait_for_upstream >> calculate_sales_performance_daily
# Note: The `PostgresOperator` requires the SQL file to be in the same directory as the DAG or provide a full path.


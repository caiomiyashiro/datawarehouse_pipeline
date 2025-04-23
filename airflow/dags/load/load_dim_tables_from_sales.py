from airflow import DAG
from airflow.providers.common.sql.operators.sql import SQLExecuteQueryOperator
from airflow.sensors.external_task import ExternalTaskSensor
import os

from datetime import datetime, timedelta

default_args = {
    'owner': os.environ.get("AIRFLOW_DEFAULT_OWNER"),
    'start_date': datetime.strptime(os.environ.get("AIRFLOW_DEFAULT_START_DATE"), '%Y-%m-%d'),
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
    'depends_on_past': True,
    'catchup': True
}

with DAG('load_dw_tables_from_sales', 
         default_args=default_args,
         schedule_interval='@daily',
         template_searchpath='/opt/sql/load') as dag:
    
    wait_for_upstream = ExternalTaskSensor(
        task_id="wait_for_stage_sales",
        external_dag_id="transform_sales",  # The DAG to monitor
        external_task_id="transform_sales", # The specific task to wait for
        allowed_states=['success'],         # Wait for success (default)
        failed_states=['failed', 'skipped'],# Fail if upstream fails/skips
        poke_interval=15,                   # Check every 15 seconds
        timeout=60*60*6,                    # Timeout after 6 hours
        mode='poke',                        # 'poke' or 'reschedule'
    )

    load_dim_country = SQLExecuteQueryOperator(
        task_id='load_countries',
        conn_id='postgres_default',
        sql='load_dim_country.sql'
    )

    load_dim_customer = SQLExecuteQueryOperator(
        task_id='load_customers',
        conn_id='postgres_default',
        sql='load_dim_customer.sql'
    )
    
    load_fact_sales = SQLExecuteQueryOperator(
        task_id='load_fact_sales',
        conn_id='postgres_default',
        sql='load_fact_sales.sql'
    )

    wait_for_upstream >> load_dim_country >> load_dim_customer >> load_fact_sales


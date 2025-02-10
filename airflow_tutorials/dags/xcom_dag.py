# xcom, branchs and trigger rules
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.bash import BashOperator
from airflow.operators.python_operator import BranchPythonOperator
from airflow.operators.dummy import DummyOperator
 
from datetime import datetime
 
def _t1(ti):
    ti.xcom_push(key='my_key', value=42)
 
def _branch(ti):
    value = ti.xcom_pull(key='my_key', task_ids='t1')
    if value == 42:
        return 't2'
    else:
        return 't3'
 
with DAG("xcom_dag", start_date=datetime(2022, 1, 1), 
    schedule_interval='@daily', catchup=False) as dag:
 
    t1 = PythonOperator(
        task_id='t1',
        python_callable=_t1
    )
 
    branch = BranchPythonOperator(
        task_id='branch',
        python_callable=_branch
    )
 
    t2 = DummyOperator(
        task_id='t2'
    )

    t3 = DummyOperator(
        task_id='t3'
    )

    t4 = DummyOperator(
        task_id='t4',
        trigger_rule='one_success'
    )
 
    t1 >> branch >> [t2, t3] >> t4
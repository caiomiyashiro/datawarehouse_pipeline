from airflow import DAG
from airflow.operators.bash import BashOperator
from groups.download_dag import download_group
from airflow.utils.task_group import TaskGroup 
from datetime import datetime
 


def transform_group():
    with TaskGroup("transform_group", tooltip='Transform Tasks') as group:
 
        transform_a = BashOperator(
        task_id='transform_a',
        bash_command='sleep 10'
    )
 
        transform_b = BashOperator(
            task_id='transform_b',
            bash_command='sleep 10'
        )
    
        transform_c = BashOperator(
            task_id='transform_c',
            bash_command='sleep 10'
        )
    return group

with DAG('group_dag', start_date=datetime(2022, 1, 1), 
    schedule_interval='@daily', catchup=False) as dag:
 
    download_tasks = download_group()
 
    check_files = BashOperator(
        task_id='check_files',
        bash_command='sleep 10'
    )
    
    transform_tasks = transform_group()
        
 
    download_tasks >> check_files >> transform_tasks
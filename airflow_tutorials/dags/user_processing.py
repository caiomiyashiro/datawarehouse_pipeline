from airflow import DAG
from datetime import datetime 
from airflow.providers.postgres.operators.postgres import PostgresOperator
from airflow.sensors.http_sensor import HttpSensor
from airflow.providers.http.operators.http import HttpOperator
from airflow.operators.python_operator import PythonOperator
from airflow.providers.postgres.hooks.postgres import PostgresHook
from airflow.utils.log.logging_mixin import LoggingMixin
from pandas import json_normalize

def _process_user(ti):
    logger = LoggingMixin().log
    logger.info(ti.xcom_pull(task_ids='extract_user'))
    logger.info('---------------------------------')
    logger.info('---------------------------------')
    user = ti.xcom_pull(task_ids='extract_user')['results'][0]
    processed_user = json_normalize({
        'first_name': user['name']['first'],
        'last_name': user['name']['last'],
        'country': user['location']['country'],
        'username': user['login']['username'],
        'password': user['login']['password'],
        'email': user['email'],
        'created_at': datetime.now()
    })
    processed_user.to_csv('/tmp/processed_user.csv', index=None, header=False)

def _store_user():
    hook = PostgresHook(postgres_conn_id='my_postgres')    
    hook.copy_expert(sql="COPY users FROM STDIN WITH DELIMITER AS ','", 
                     filename='/tmp/processed_user.csv')

with DAG('user_processing',
          start_date=datetime(2024, 1, 1), 
          schedule_interval='@daily',
          catchup=False) as dag:
    
    create_table = PostgresOperator(
        task_id='create_table', 
        postgres_conn_id='my_postgres',
        sql='''
        CREATE TABLE IF NOT EXISTS users (
            firstname TEXT NOT NULL,
            lastname TEXT NOT NULL,
            country TEXT NOT NULL,
            username TEXT NOT NULL,
            password TEXT NOT NULL,
            email TEXT NOT NULL,
            created_at TIMESTAMP NOT NULL
        );
        '''
    )

    is_api_available = HttpSensor(
        task_id='is_api_available',
        http_conn_id='user_api',
        endpoint='api/'
    )

    extract_user = HttpOperator(
        task_id='extract_user',
        http_conn_id='user_api',
        endpoint='api/',
        method='GET',
        response_filter=lambda response: response.json(),
        log_response=True
    )

    process_user = PythonOperator(
        task_id='process_user',
        python_callable=_process_user
    )

    store_user = PythonOperator(
        task_id='store_user',
        python_callable=_store_user
    )

    create_table >> is_api_available >> extract_user >> process_user >> store_user

if __name__ == "__main__":
    dag.test()    
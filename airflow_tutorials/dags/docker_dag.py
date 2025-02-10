from airflow import DAG
from airflow.providers.docker.operators.docker import DockerOperator

 
from datetime import datetime

 
with DAG("docker_dag", start_date=datetime(2022, 1, 1), 
    schedule_interval='@daily', catchup=False) as dag:
    
    hello_world_task = DockerOperator(
        task_id='docker_hello_world',
        image='hello-world',
        docker_url='unix://var/run/docker.sock',
        network_mode='bridge',
        auto_remove=True
    )

"""
To configure Airflow running inside a Docker Compose setup and using Celery to run a DockerOperator, follow these steps:

## Docker Compose Setup

1. Create a `docker-compose.yaml` file with the following services:
   - Airflow Webserver
   - Airflow Scheduler
   - Airflow Worker (Celery)
   - Redis (as message broker for Celery)
   - PostgreSQL (as metadata database)

2. Download the official `docker-compose.yaml` file:

```bash
curl -LfO 'https://airflow.apache.org/docs/apache-airflow/stable/docker-compose.yaml'
```

3. Create necessary directories:

```bash
mkdir -p ./dags ./logs ./plugins
```

4. Set the `AIRFLOW_UID` environment variable:

```bash
echo -e "AIRFLOW_UID=$(id -u)" > .env
```

## Customizing Airflow Image

Create a custom Dockerfile to include the Docker provider:

```dockerfile
FROM apache/airflow:2.6.1
RUN pip install apache-airflow-providers-docker
```

## Configuration

1. Modify the `docker-compose.yaml` file to use your custom image and enable Celery:

```yaml
version: '3'
services:
  airflow-webserver:
    image: your-custom-airflow-image:latest
    # ... other configurations ...

  airflow-scheduler:
    image: your-custom-airflow-image:latest
    # ... other configurations ...

  airflow-worker:
    image: your-custom-airflow-image:latest
    command: celery worker
    # ... other configurations ...

  airflow-init:
    image: your-custom-airflow-image:latest
    # ... other configurations ...

  redis:
    image: redis:latest
    # ... other configurations ...

  postgres:
    image: postgres:13
    # ... other configurations ...
```

2. Configure Airflow to use Celery and Redis in the `docker-compose.yaml`:

```yaml
x-airflow-common:
  &airflow-common
  # ... other configurations ...
  environment:
    &airflow-common-env
    AIRFLOW__CORE__EXECUTOR: CeleryExecutor
    AIRFLOW__CELERY__BROKER_URL: redis://redis:6379/0
    AIRFLOW__CELERY__RESULT_BACKEND: db+postgresql://airflow:airflow@postgres/airflow
    # ... other environment variables ...
```

## Running DockerOperator

1. In your DAG file, import the necessary modules:

```python
from airflow import DAG
from airflow.providers.docker.operators.docker import DockerOperator
```

2. Configure the DockerOperator in your DAG:

```python
docker_task = DockerOperator(
    task_id='docker_task',
    image='your-docker-image:tag',
    command='/bin/bash -c "echo hello"',
    network_mode='bridge',
    docker_url='unix://var/run/docker.sock',
    # ... other configurations ...
)
```

3. Ensure the Docker socket is accessible to the Airflow worker container by adding a volume mount in the `docker-compose.yaml`:

```yaml
services:
  airflow-worker:
    # ... other configurations ...
    volumes:
      - /var/run/docker.sock:/var/run/docker.sock
```

## Starting Airflow

1. Initialize the Airflow database:

```bash
docker-compose up airflow-init
```

2. Start all services:

```bash
docker-compose up -d
```

3. Access the Airflow web UI at `http://localhost:8080` with default credentials `airflow/airflow`[1][2].

By following these steps, you'll have Airflow running inside Docker Compose, using Celery for task distribution, and capable of executing DockerOperator tasks. Remember to adjust configurations based on your specific requirements and security considerations[3][4].

Citations:
[1] https://www.restack.io/docs/airflow-knowledge-docker-compose-setup-production-github-google-cloud-composer-ubuntu-deploy-file-example
[2] https://airflow.apache.org/docs/apache-airflow/stable/howto/docker-compose/index.html
[3] https://airflow.apache.org/docs/apache-airflow/2.6.0/howto/docker-compose/index.html
[4] https://www.restack.io/docs/airflow-knowledge-apache-docker-provider-pypi
[5] https://qiita.com/v1tam1n/items/246b533234a49045a38e
[6] https://zenn.dev/notrogue/articles/7234dff0856b59
[7] https://zenn.dev/c6tower/scraps/be51eb8c86a697
[8] https://qiita.com/yuuman/items/a449bbe36710ad837df7
"""
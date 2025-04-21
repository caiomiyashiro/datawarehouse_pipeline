#!/bin/bash

echo "Creating Airflow connection to PostgreSQL..."

# Load .env variables from parent directory
set -a
source ../.env
set +a

# Name of your Airflow service (adjust if needed)
AIRFLOW_WEBSERVER_SERVICE=$AIRFLOW_WEBSERVER_SERVICE

# Run the Airflow CLI in the container to add the connection
docker compose exec $AIRFLOW_WEBSERVER_SERVICE airflow connections add "$AIRFLOW_CONN_ID" \
    --conn-type "$AIRFLOW_CONN_TYPE" \
    --conn-login "$POSTGRES_USER" \
    --conn-password "$POSTGRES_PASSWORD" \
    --conn-host "$POSTGRES_HOST" \
    --conn-port "$POSTGRES_PORT" \
    --conn-schema "$POSTGRES_DATA_DB"

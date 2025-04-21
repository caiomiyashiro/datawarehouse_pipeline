#!/bin/bash
echo "Running SQL scripts in custom order..."

# # Database connection info
# DB_NAME="${POSTGRES_DB:-postgres}"
# DB_USER="${POSTGRES_USER:-airflow}"

#!/bin/bash

echo "Running SQL scripts in custom order..."

# Execute SQL scripts in the desired order
psql -U "$POSTGRES_USER" -d "$POSTGRES_DATA_DB" -f /docker-entrypoint-initdb.d/create_schemas/create_schemas.sql
psql -U "$POSTGRES_USER" -d "$POSTGRES_DATA_DB" -f /docker-entrypoint-initdb.d/create_tables/sales_tables.sql
psql -U "$POSTGRES_USER" -d "$POSTGRES_DATA_DB" -f /docker-entrypoint-initdb.d/create_tables/dim_customer.sql
psql -U "$POSTGRES_USER" -d "$POSTGRES_DATA_DB" -f /docker-entrypoint-initdb.d/create_tables/dim_country.sql
psql -U "$POSTGRES_USER" -d "$POSTGRES_DATA_DB" -f /docker-entrypoint-initdb.d/create_tables/add_foreign_keys.sql

# I should run this as an airflow backfill
# psql -U "$POSTGRES_USER" -d "$POSTGRES_DB" -f /docker-entrypoint-initdb.d/create_tables/agg_sales_perf_monthly.sql  
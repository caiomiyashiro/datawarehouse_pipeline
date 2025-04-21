# ETL POC

---

# Retail Data Pipeline with Apache Airflow  
**Automated ETL pipeline for retail data generation, transformation, and analysis.**  

---

## **Project Overview**  
This project automates the generation and transformation of simulated retail sales data using Apache Airflow. It includes:  
- **Data Extration and Generation**: Simulates retail transactions (sales, customers, products).  
- **Data Transformation**: Cleans, aggregates, and prepares data for analytics.
- **Data Loading**: Loads data into datawarehouse system. 
- **Workflow Orchestration**: Scheduled DAGs to manage ETL processes.  

For more information about how to add a DAG, please refer [here](docs/adding_dags.md)

---

## **Key Features**  
- **Celery Executor**: Parallel task execution with Redis and PostgreSQL.  
- **Modular DAGs**: Reusable workflows for data generation and transformation.  
- **Backfill Support**: Reprocess historical data with `--reset-dagruns`.  
- **Dockerized**: Isolated environment with Airflow, PostgreSQL, and Redis.  

---

## **Tech Stack**  
| **Component**       | **Technology**          |  
|----------------------|-------------------------|  
| Workflow Orchestration | Apache Airflow 2.10.5 |  
| Database              | PostgreSQL 13           |  
| Queueing System       | Redis 7.2              |  
| Containerization      | Docker Compose         |  
| Data Processing      | Python and SQL         | 

---

## **Quick Start**  
### **Prerequisites**  
- Docker & Docker Compose ([Install Guide](https://docs.docker.com/get-docker/))  
- Python 3.8+ (for local development)  

### **2. Configure Environment**  
Create a `.env` file. You can use `.env_temp` as a reference for the needed environment variables:  

### **3. Start Services**  
```bash  
docker compose up -d --build
```  

#### 3.a. Docker compose will start the following services:  

| **Service**       | **Port**          |  
|-------------------|-------------------|  
| postgres          | 5432     |  
| adminer           | 8079     |  
| redis             | 6379     |  
| airflow-webserver | 8080     |  
| airflow-scheduler |          | 
| airflow-worker    |          | 
| airflow-triggerer |          | 
| airflow-cli       |          | 

#### 3.b. Postgres will execute `sql/initialize_tables.sh`  

* Create schemas  
* Create tables in different schemas
* Create foreign keys

### **4. Manually set Postgress connection with Airflow**

```bash  
./airflow/local_scripts/initialize_airflow_postgres_connection.sh
```  

### **5. Access Airflow UI**  
Visit `http://localhost:8080` and log in with:  
- **Username**: check `_AIRFLOW_WWW_USER_USERNAME` in .env
- **Password**: check `_AIRFLOW_WWW_USER_PASSWORD` in .env 

---

## **Project Structure**  
```  
.
├── airflow.cfn                          # Airflow configuration file
├── airflow.dockerfile                   # Custom Dockerfile for building the Airflow image
├── config/                              # Airflow configuration overrides and custom settings
├── dags/                                # Airflow DAGs (organized by ETL phase)
│   ├── extract/                         # DAG/tasks for extracting data from source systems
│   ├── load/                            # DAG/tasks for loading dimension tables
│   └── transform/                       # DAG/tasks for transforming raw sales data
├── data/                                # Sample data and notebooks
├── docker-compose.yaml                  # Docker Compose setup for Airflow and dependencies
├── local_scripts/                       # Utility scripts for local setup
│   └── initialize_airflow_postgres_connection.sh # Script to initialize Airflow Postgres connection
├── plugins/                             # Custom Airflow plugins
├── python/                              # Python modules for ETL logic
├── sql/                                 # SQL scripts for schema, table creation, and ETL
```

---

## **Data Pipeline Overall Architecture**  
```mermaid  
graph TD  
  A[Source Data] -->|Extract| B[PostgreSQL [raw]]  
  B -->|Transform| C[PostgreSQL [stage]]  
  C -->|Load / Aggregate| D[PostgreSQL [dw]]  
```
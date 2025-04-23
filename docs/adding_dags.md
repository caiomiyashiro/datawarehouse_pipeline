# ETL Data Layers Overview

Our ETL process logically separates data into three key layers: **Raw**, **Stage**, and **Data Warehouse (DW)**. This organization ensures data quality, traceability, and efficient analytics.

## 1. Raw Layer
- **Description:** The raw layer stores data exactly as it is extracted from source systems, without any modification.
- **Purpose:**  
  - Preserve original data for auditing and troubleshooting.  
  - Serve as a backup to enable reprocessing if needed.  
- **Characteristics:**  
  - Data is unaltered and stored in its native format.  
  - Minimal constraints or transformations applied.

## 2. Stage (Staging) Layer
- **Description:** The staging layer is an intermediate area where raw data undergoes initial cleaning and preparation.
- **Purpose:**  
  - Perform light transformations such as filtering, deduplication, and validation.  
  - Prepare data for more complex transformations and loading into the warehouse.  
- **Characteristics:**  
  - Data is partially processed but not yet business-ready.  
  - Acts as a buffer for troubleshooting and quality checks.

## 3. Data Warehouse (DW) Layer
- **Description:** The data warehouse is the final destination for fully transformed and modeled data.
- **Purpose:**  
  - Provide clean, consistent, and aggregated data optimized for reporting and analytics.  
  - Support business intelligence and decision-making processes.  
- **Characteristics:**  
  - Data is structured using dimensional models (snowflake schema).  
  - High-quality, validated, and ready for consumption by end-users.

---

By maintaining these distinct layers, the ETL process ensures data integrity, flexibility in processing, and reliable analytics outputs.

---

# DAGs Organization

The `dags` folder contains the python Airflow code used to orchestrate the ETL steps.  
- Depending on the need of the DAG, add it to the respective folder: `extract`, `transform`, or `load`.  
- DAGs will call tasks and the execution type will depend on how it was programmed (Python or SQL, or else)
- Do **not** add other files than the DAG files. 
- Add the task scripts in the corresponding `python` or `sql` folders (or something else), also respecting their overall goal `extract`, `transform`, or `load`.

# File Naming

Valid for DAG files and task files.  

* snake_case  
* first word represent which ETL step they are executing, e.g., `extract_sales.py`, `transform_sales_data.py`  

# DAGs parameters and samples

For parameters and sample function explanations, please refer to the code and comments present in the sample ETL process for sales data:  

* `dags/extract/sales.py`
* `dags/transform/transform_raw_sales.py`
* `dags/load/load_dim_tables_from_sales.py`  
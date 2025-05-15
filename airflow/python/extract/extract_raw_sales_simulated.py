import pandas as pd
import psycopg2
from psycopg2 import sql
import numpy as np
from datetime import datetime
import sys
import time
import os
import jsonschema
import json
import csv
from sqlalchemy import create_engine, inspect
from sqlalchemy.exc import ProgrammingError, IntegrityError

sys.path.append('/opt/data')
sys.path.append('/opt/contracts/extract')

def postgres_2_df(
    conn_params: dict,
    table_name: str,
    schema: str = None,
    target_where_column: str = None,
    target_where_value: str = None) -> pd.DataFrame:
    """
    Read a PostgreSQL table into a pandas DataFrame using connection parameters.
    Args:
        conn_params (dict): Dictionary with keys: dbname, user, password, host, port.
        table_name (str): Name of the target SQL table.
        schema (str): PostgreSQL schema to read the table from.
        target_date (str): Date to filter the data (YYYY-MM-DD).
    Returns:
        pd.DataFrame: DataFrame containing the data from the PostgreSQL table.
    """
    conn_str = (
        f"postgresql+psycopg2://{conn_params['user']}:{conn_params['password']}@"
        f"{conn_params['host']}:{conn_params['port']}/{conn_params['dbname']}"
    )

    engine = create_engine(conn_str)

    # Compose full table name with optional schema
    full_table_name = f'{schema}.{table_name}' if schema else table_name

    # Optional filtering
    query = f"SELECT * FROM {full_table_name}"
    if target_where_column:
        query += f""" WHERE "{target_where_column}"::DATE = DATE '{target_where_value}'"""
    print(f'------ Executing query: {query}')
    df = pd.read_sql(query, con=engine)
    return df

def df_2_postgres(
    df: pd.DataFrame,
    table_name: str,
    target_date_str: str,
    conn_params: dict,
    schema: str = None  
):
    """
    Create or replace a PostgreSQL table from a pandas DataFrame using connection parameters.

    Args:
        df (pd.DataFrame): The DataFrame to write.
        table_name (str): Name of the target SQL table.
        conn_params (dict): Dictionary with keys: dbname, user, password, host, port.
        if_exists (str): 'fail', 'replace', or 'append'.
        schema (str): PostgreSQL schema to write the table into.
    """

    conn_str = (
        f"postgresql+psycopg2://{conn_params['user']}:{conn_params['password']}@"
        f"{conn_params['host']}:{conn_params['port']}/{conn_params['dbname']}"
    )

    engine = create_engine(conn_str)

    try:
        # Attempt to create the table (just the structure)
        df.head(0).to_sql(
            name=table_name,
            con=engine,
            index=False,
            if_exists='fail',  # only create if it doesn't exist
            schema=schema
        )
    except (ProgrammingError, IntegrityError):
        # Table probably exists already — safe to ignore
        pass
    except ValueError as e:
        # pandas may raise ValueError if table exists
        if "Table" in str(e) and "already exists" in str(e):
            pass
        else:
            raise

    # Step 2: Delete old data for target_date
    with engine.begin() as conn:
        full_table_name = f'"{schema}".{table_name}' if schema else table_name
        delete_query = f"""
            DELETE FROM {full_table_name}
            WHERE DATE("InvoiceDate") = DATE('{target_date_str}')
        """
        conn.execute(delete_query, {"target_date": target_date_str})

    df.to_sql(
        name=table_name,
        con=engine,
        index=False,
        if_exists='append',
        schema=schema
    )

    # print(f"✅ Table '{schema}.{table_name}' written to database '{conn_params['dbname']}' ({if_exists}).")


# write check_if_data_exists method to check if data exists in the database. If it does return False
def check_if_data_exists(target_date:str, conn_params=None, table_name:str='sales'):
    """
    Parameters:
        target_date: The date to be processed by DAG (YYYY-MM-DD)
        conn_params: PostgreSQL connection parameters
        table_name: Target table name in database
    """
    
    try:
        with psycopg2.connect(**conn_params) as conn:
            with conn.cursor() as cur:
                # Check if date exists in database
                check_query = sql.SQL("""
                    SELECT EXISTS (
                        SELECT 1 FROM {}.{} 
                        WHERE DATE(invoicedate) = %s
                    )
                """).format(
                    sql.Identifier('raw'),
                    sql.Identifier(table_name))
                
                cur.execute(check_query, (target_date,))
                continue_downstream = cur.fetchone()[0]
                if continue_downstream:
                    print(f"Data for {target_date} already exists in the database. Skipping.")
                    continue_downstream = False
                else:
                    print(f"No data for {target_date} found in the database.")
                    continue_downstream = True
                return continue_downstream
    except Exception as e:
        print(f"Database error: {e}")
        raise
    finally:
        if 'conn' in locals():
            conn.close()

def generate_daily_data(sample_data_filename:str, target_date:str,
                       conn_params=None, table_name:str='sales'):
    """
    Parameters:
        sample_data: DataFrame filename containing retail sample data
        target_date: The date to be processed by DAG (YYYY-MM-DD)
        days_back: Number of days to process from execution date
        conn_params: PostgreSQL connection parameters
        table_name: Target table name in database
    """
    
    # Load sample data    
    sample_data = pd.read_csv('/opt/data/'+sample_data_filename)
    # Convert InvoiceDate to datetime
    if not np.issubdtype(sample_data['InvoiceDate'].dtype, np.datetime64):
        sample_data['InvoiceDate'] = pd.to_datetime(sample_data['InvoiceDate'])

    target_date = datetime.strptime(target_date, '%Y-%m-%d').date()
    day_str = target_date.strftime('%Y-%m-%d')
    # Dynamic sample size between a range
    rng = np.random.default_rng(time.time_ns()) 
    sample_size = rng.integers(600, 1000)
    sample_indices = np.random.choice(
        sample_data.index,
        size=sample_size,
        replace=False
    )

    # Create copy of sampled data with modified dates
    sampled_data = sample_data.loc[sample_indices].copy()
    sampled_data['InvoiceDate'] = pd.to_datetime(
        sampled_data['InvoiceDate'].dt.strftime('%H:%M:%S').apply(
            lambda x: f"{day_str} {np.random.randint(0,24):02d}:{np.random.randint(0,60):02d}:{np.random.randint(0,60):02d}"
        )
    )

    # Remove auto-generated key from dataframe
    sampled_data.drop(columns='InvoiceNo', inplace=True, errors='ignore')

    # Save sampled data to csv. In production, this would be saved to a temp database area
    # for further processing or validation, such as data contracts
    df_2_postgres(
        df=sampled_data,
        table_name=table_name,
        target_date_str=day_str,
        conn_params=conn_params,
        schema='validation'
    )
    print(f"Sampled data saved to table 'validation.'{table_name}")

# method to validate the data based on data contract
def validate_sales_data(table_name:str,
                        target_date:str,
                        schema:str='validation',  
                        sales_contract_filename:str='extract_sales_contract.json',
                        conn_params: dict=None):
    """
    Parameters:
        table_name: Target table name in database
        target_date: The date to be processed by DAG (YYYY-MM-DD)
        conn_params: PostgreSQL connection parameters
    """
    # Load contract schema
    with open(f'/opt/contracts/extract/{sales_contract_filename}', encoding="utf-8") as f:
        sales_data_contract = json.load(f)

    # Load your extracted sales data for the day
    df = postgres_2_df(
        conn_params=conn_params,
        table_name=table_name,
        schema=schema,
        target_where_column="InvoiceDate",
        target_where_value=target_date)
    # pandas datetime is not recognized by JSON validation. Convert it to ISO 8601 format
    df['InvoiceDate'] = df['InvoiceDate'].dt.strftime('%Y-%m-%dT%H:%M:%S')  # ISO 8601 without timezone
    
    # Convert DataFrame to list of dictionaries
    records = df.to_dict(orient='records')
    # Validate each record against the contract
    for record in records:
        try:
            jsonschema.validate(instance=record, schema=sales_data_contract)
        except jsonschema.ValidationError as e:
            # Handle validation error (log, alert, quarantine, etc.). Data could be quarantined, ignoring
            # in this POC.
            # raise ValueError(f"Data contract validation failed: {e.message}") from e
            # continue_downstream = False
            print(f"-------- Data contract validation failed:\nrecord: {record}\n{e.message}\n\n")
    
    continue_downstream = True # in POC we're always returning True
    # if any validation errors were found, set continue_downstream to False
    return continue_downstream

def insert_daily_data(target_date:str,
                      conn_params=None, 
                      table_name:str='sales'):
    """
    Parameters:
        target_date: The date to be processed by DAG (YYYY-MM-DD)
        conn_params: PostgreSQL connection parameters
        table_name: Target table name in database
    """
    
    sample_data = pd.read_csv(f'/opt/data/{table_name}_{target_date}.csv')
    # Convert InvoiceDate to datetime
    if not np.issubdtype(sample_data['InvoiceDate'].dtype, np.datetime64):
        sample_data['InvoiceDate'] = pd.to_datetime(sample_data['InvoiceDate'])

    try:
        target_date = datetime.strptime(target_date, '%Y-%m-%d').date()
        
        with psycopg2.connect(**conn_params) as conn:
            with conn.cursor() as cur:
                day_str = target_date.strftime('%Y-%m-%d')
                # Prepare insertion
                cols = [col.lower() for col in sample_data.columns.tolist()]
                placeholders = sql.SQL(',').join([sql.Placeholder()] * len(cols))
                
                insert_query = sql.SQL("""
                    INSERT INTO {}.{} ({}) 
                    VALUES ({})
                """).format(
                    sql.Identifier('raw'),
                    sql.Identifier(table_name),
                    sql.SQL(',').join(map(sql.Identifier, cols)),
                    placeholders
                )

                # Execute insertion
                tuples = [tuple(x) for x in sample_data.to_numpy()]
                cur.executemany(insert_query, tuples)
                conn.commit()
                print(f"Inserted {len(sample_data)} records for {day_str}")

    except Exception as e:
        print(f"Database error: {e}")
        raise
    finally:
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    # Load data

    # Execute processing
    insert_sampled_data(sample_data_filename="Online_Retail_cleaned.csv",
                        target_date=datetime.today().strftime('%Y-%m-%d'))

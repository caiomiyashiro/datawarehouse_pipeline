import pandas as pd
import psycopg2
from psycopg2 import sql
import numpy as np
from datetime import datetime
import sys
import time

def insert_sampled_data(sample_data_filename:str, target_date:str,
                       conn_params=None, table_name:str='sales'):
    """
    Parameters:
        sample_data: DataFrame filename containing retail sample data
        target_date: The date to be processed by DAG (YYYY-MM-DD)
        days_back: Number of days to process from execution date
        conn_params: PostgreSQL connection parameters
        table_name: Target table name in database
    """
    if conn_params is None:
        conn_params = {
            'dbname': 'postgres',
            'user': 'airflow',
            'password': 'airflow',
            'host': 'localhost',
            'port': 5432
        }

    sys.path.append('/opt/data')    
    sample_data = pd.read_csv('/opt/data/'+sample_data_filename)
    # Convert InvoiceDate to datetime
    if not np.issubdtype(sample_data['InvoiceDate'].dtype, np.datetime64):
        sample_data['InvoiceDate'] = pd.to_datetime(sample_data['InvoiceDate'])

    try:
        # Calculate target dates based on execution date
        target_date = datetime.strptime(target_date, '%Y-%m-%d').date()
        
        with psycopg2.connect(**conn_params) as conn:
            with conn.cursor() as cur:
                day_str = target_date.strftime('%Y-%m-%d')

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
                exists = cur.fetchone()[0]

                if exists:
                    print(f"Data for {day_str} already exists. Skipping.")
                else:
                    # Dynamic sample size between 15k-18k
                    
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


                    # Prepare insertion
                    cols = [col.lower() for col in sampled_data.columns.tolist()]
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
                    tuples = [tuple(x) for x in sampled_data.to_numpy()]
                    cur.executemany(insert_query, tuples)
                    conn.commit()
                    print(f"Inserted {len(sampled_data)} records for {day_str}")

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

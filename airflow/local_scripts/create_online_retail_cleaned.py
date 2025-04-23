import pandas as pd
import numpy as np

import random
from datetime import datetime, timedelta

import random
from datetime import date, datetime, timedelta

import random
from datetime import datetime, timedelta

df = pd.read_csv('../data/Online_Retail.csv', encoding='utf-8', sep=',')

def random_datetimes(start_date: datetime.date, end_date:datetime.date, n:int):
    """
    Generate n random datetimes between start_date and end_date.
    Dates are sampled uniformly, then random times are added.
    
    :param start_date_str: The start date as string 'yyyy-mm-dd' (inclusive)
    :param end_date_str: The end date as string 'yyyy-mm-dd' (inclusive)
    :param n: Number of random datetimes to generate
    :return: List of random datetime objects
    """
    
    date_range = (end_date - start_date).days + 1  # +1 to include end_date
    random_datetimes = []
    
    for _ in range(n):
        # Sample a random date
        random_days = random.randint(0, date_range - 1)
        random_date = start_date + timedelta(days=random_days)
        
        # Generate random time
        random_hour = random.randint(0, 23)
        random_minute = random.randint(0, 59)
        random_second = random.randint(0, 59)
        
        # Combine date and time
        random_datetime = datetime.combine(random_date, 
                                           datetime.min.time()) + \
                          timedelta(hours=random_hour, 
                                    minutes=random_minute, 
                                    seconds=random_second)
        
        random_datetimes.append(random_datetime)
    
    return sorted(random_datetimes)


# example
# one_month_ago = '2024-07-01'
# yesterday = '2024-07-31'
today = date.today()
yesterday = today - timedelta(days=1)
one_month_ago = today - timedelta(days=30)
print(f'From {one_month_ago} to {yesterday}')

# removing duplicate order_number for simplification
df = df.drop_duplicates(subset=['InvoiceNo'], keep='last')

num_samples = df.shape[0]                       
r_datetimes = random_datetimes(one_month_ago, yesterday, num_samples)

df['InvoiceDate'] = r_datetimes

# many rows have description with quotes and inside commas "description, description".
mask = (df['Description'].isna() & df['StockCode'].isna())
# display(df.loc[mask].head())

# For now, we just remove them
df = df[~mask]


# some rows have StockCode = some long description or different country when == POSTAGE
mask = ((df['StockCode'].str.len() > 10) | (df['StockCode'] == 'POST'))
# display(df.loc[mask].head())
# print(sum(mask))

# For now, we just remove them
df = df[~mask]



# drop inf and -inf
df.replace([np.inf, -np.inf], np.nan, inplace=True)
df = df.dropna(subset=['CustomerID', 'Quantity']).copy()

# convert to integers
df["Quantity"] = df["Quantity"].astype(int)
df["CustomerID"] = df["CustomerID"].astype(int)

# drop duplicates
# df = df.drop_duplicates(subset=['InvoiceDate', 'InvoiceNo'])

df.to_csv('../data/Online_Retail_cleaned.csv', index=False)
print(f"Data cleaned and saved to ../data/Online_Retail_cleaned.csv")
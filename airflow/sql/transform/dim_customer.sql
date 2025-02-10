-- Create a temporary table with row numbers
CREATE TEMPORARY TABLE raw_sales_ranked AS (
    SELECT 
        CustomerID,
        Country,
        -- other columns if you want to update them
        ROW_NUMBER() OVER (
            PARTITION BY CustomerID, Country
            ORDER BY InvoiceDate DESC
        ) AS row_num
    FROM raw_sales
    WHERE InvoiceDate = {prev_ds}
);

-- Select all rows except duplicates
CREATE TEMPORARY TABLE raw_sales_deduped AS (
    SELECT 
        CustomerID,
        Country,
    FROM raw_sales_ranked
    WHERE row_num = 1
);

-- -- Update Customer Dimension (SCD Type 2) focusing on Country changes
-- Step 1: Close out any existing active records where Country has changed
UPDATE dim_customer d
SET 
    end_date = CURRENT_DATE - INTERVAL '1 day'
FROM raw_sales_deduped s
WHERE d.customer_id = s.customer_id
    AND d.country != s.country;

-- Step 2: Insert new records for customers whose Country has changed
INSERT INTO dim_customer (
    customer_id,
    country,
    end_date
)
SELECT 
    s.CustomerID,
    s.Country,
    NULL as end_date,
FROM raw_sales_deduped s
LEFT JOIN dim_customer d 
    ON s.CustomerID = d.customer_id 
    AND d.end_date IS NULL
WHERE d.customer_id IS NULL OR d.country != s.country;

-- Step 3: Insert new customers
INSERT INTO dim_customer (
    customer_id,
    country,
    end_date
)
SELECT 
    s.CustomerID,
    s.Country,
    NULL as end_date
FROM raw_sales_deduped s
LEFT JOIN dim_customer d ON s.customer_id = d.customer_id
WHERE d.customer_id IS NULL;

-- -- Step 4: Update other attributes for current records (SCD Type 1 for non-Country attributes)
-- -- UPDATE dim_customer d
-- -- SET 
-- --     customer_name = s.customer_name,
-- --     email = s.email,
-- --     address = s.address
-- -- FROM stage_customer s
-- -- WHERE d.customer_id = s.customer_id
-- --     AND d.is_current = 1
-- --     AND d.country = s.country
-- --     AND (
-- --         d.customer_name != s.customer_name OR
-- --         d.email != s.email OR
-- --         d.address != s.address
-- --     );
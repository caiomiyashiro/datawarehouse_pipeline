-- Create a temporary table with row numbers
CREATE TEMPORARY TABLE raw_sales_ranked AS (
    SELECT 
        customerid  AS customer_id,
        country     AS country,
        -- other columns if you want to update them
        ROW_NUMBER() OVER (
            PARTITION BY customerid
            ORDER BY invoicedate DESC
        ) AS row_num
    FROM raw.sales
    WHERE DATE(invoicedate) = '{{ds}}'::DATE
);

-- Select all rows except duplicates
CREATE TEMPORARY TABLE raw_sales_deduped AS (
    SELECT 
        customer_id,
        country
    FROM raw_sales_ranked
    WHERE row_num = 1
);

-- -- Update Customer Dimension (SCD Type 2) focusing on Country changes
-- Step 1: Close out any existing active records where Country has changed
UPDATE dw.dim_customer d
SET end_date = CURRENT_DATE - INTERVAL '1 day'
FROM raw_sales_deduped s, dw.dim_country c
WHERE d.customer_id = s.customer_id
  AND d.country_id = c.country_id
  AND d.end_date IS NULL
  AND c.country_name != s.country;



-- Step 2: Insert new records for customers whose Country has changed
INSERT INTO dw.dim_customer (
    customer_id,
    customer_name,
    customer_email,
    country_id,
    end_date
)
SELECT 
    s.customer_id                               AS customer_id,
    'name_' || s.customer_id                    AS customer_name,
    'email_' || s.customer_id || '@example.com' AS customer_email,
    c.country_id                                AS country_id,
    NULL                                        AS end_date
FROM raw_sales_deduped s
LEFT JOIN dw.dim_customer d 
    ON s.customer_id = d.customer_id 
    AND d.end_date IS NULL
LEFT JOIN dw.dim_country c 
    ON s.country = c.country_name
WHERE (d.customer_id IS NULL OR d.country_id != c.country_id)
  AND c.country_id IS NOT NULL;
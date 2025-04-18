-- Step 1: Delete existing records for the target date
DELETE FROM dw.fact_sales
WHERE DATE(invoice_date) >= '{{ ds }}'::timestamp  -- Start of day
  AND DATE(invoice_date) < '{{ ds }}'::timestamp + INTERVAL '1 day';  -- End of day

-- Create a temporary table with row numbers
CREATE TEMPORARY TABLE dim_customer_valid AS (
    SELECT 
        customer_sk     AS customer_sk,
        customer_id     AS customer_id,
        country_id      AS country_id
    FROM dw.dim_customer
    WHERE DATE(end_date) IS NULL -- only include active records
);

-- Step 2: Insert transformed data
-- fact_sales_transformation.sql
-- There might be customers with changing country within 1 day. customer_sk represents the latest country in that day.
CREATE TEMPORARY TABLE transformed_sales AS (
    SELECT    
        s.invoiceno     as invoice_number,
        s.stockcode     as stock_code,
        s.description   as sale_description,
        s.quantity      as quantity,
        s.invoicedate   as invoice_date,
        s.unitprice     as unit_price,
        d.customer_sk   as customer_sk,
        c.country_id
    FROM raw.sales s
    LEFT JOIN dw.dim_country c 
        ON s.country = c.country_name
    LEFT JOIN dim_customer_valid d 
        ON s.customerid = d.customer_id
    WHERE c.country_id IS NOT NULL
        AND d.customer_sk IS NOT NULL
        AND DATE(s.invoicedate) = '{{ ds }}'::date  -- Parameterized filter
);

INSERT INTO dw.fact_sales (
    invoice_number,
    stock_code,
    sale_description,
    quantity,
    invoice_date,
    unit_price,
    customer_sk,
    country_id
)
SELECT 
    ts.invoice_number,
    ts.stock_code,
    ts.sale_description,
    ts.quantity,
    ts.invoice_date,
    ts.unit_price,
    ts.customer_sk,
    ts.country_id
FROM transformed_sales ts;



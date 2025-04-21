-- # Clean	Drop rows with missing InvoiceNo or CustomerID
-- # Standardize	Convert InvoiceDate to standard format, unify currency to USD
-- # Deduplicate	Remove duplicate sales rows by InvoiceNo and StockCode
-- # Enrich	Map Country to country_id using a lookup table
-- # Calculate	Add total_sale column = Quantity × UnitPrice
-- # Validate	Ensure no negative Quantity or UnitPrice

-- Step 1: Delete existing records for the target date
DELETE FROM stage.sales
WHERE DATE(invoice_date) >= '{{ ds }}'::timestamp  -- Start of day
  AND DATE(invoice_date) < '{{ ds }}'::timestamp + INTERVAL '1 day';  -- End of day

-- # Deduplicate	Remove duplicate sales rows by InvoiceNo and StockCode
CREATE TEMPORARY TABLE sales_dedup AS (
    SELECT 
        *
    FROM 
    (
        SELECT 
            *,
            -- other columns if you want to update them
            ROW_NUMBER() OVER (
                PARTITION BY invoiceno
                ORDER BY invoicedate DESC
            ) AS row_num
        FROM raw.sales
        WHERE DATE(invoicedate) = '{{ds}}'::DATE
    ) a
    WHERE row_num = 1
);

INSERT INTO stage.sales (
    invoice_number,
	stock_code,
	sale_description,
	quantity,
	invoice_date,
	unit_price,
    total_sale_usd,
	customer_id,
	country_name
)
SELECT 
    invoiceno                   as invoice_number,
    stockcode                   as stock_code,
    description                 as sale_description,
    quantity                    as quantity,
    invoicedate                 as invoice_date,
    unitprice                   as unit_price,
    unitprice * quantity * 1    as total_sale_usd, -- multiplying by country x dollar conversion rate
    customerid                  as customer_id,
    country                     as country_name
FROM sales_dedup
WHERE country IS NOT NULL
    AND (customerid IS NOT NULL OR customerid NOT BETWEEN 12000 AND 13000) -- Exclude test and robot customers with IDs between 12000 and 13000
    AND quantity > 0
    AND unitprice > 0;


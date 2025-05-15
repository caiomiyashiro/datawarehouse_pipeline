-- Step 1: Delete existing records for the target date
DELETE FROM raw.sales
WHERE DATE(invoicedate) >= '{{ ds }}'::timestamp  -- Start of day
  AND DATE(invoicedate) < '{{ ds }}'::timestamp + INTERVAL '1 day';  -- End of day

INSERT INTO raw.sales (
    stockcode,
    description,
    quantity,
    invoicedate,
    unitprice,
    customerid,
    country
)
SELECT
    "StockCode",
    "Description",
    "Quantity",
    "InvoiceDate",
    "UnitPrice",
    "CustomerID",
    "Country"
FROM validation.sales;

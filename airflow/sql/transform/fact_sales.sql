CREATE TABLE fact_sales (
    InvoiceNo VARCHAR(10),
    StockCode VARCHAR(10),
    Description VARCHAR(255),
    Quantity INT,
    InvoiceDate TIMESTAMP,
    UnitPrice DECIMAL(10, 2),
    CustomerID INT,
    PRIMARY KEY (invoicedate, InvoiceNo)
);


INSERT INTO fact_sales (
    invoice_date,
    invoice_number,
    customer_id,
    stock_code,
    description, 
    quantity,
    unit_price
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
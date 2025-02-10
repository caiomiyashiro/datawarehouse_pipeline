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

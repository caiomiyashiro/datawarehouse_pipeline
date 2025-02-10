CREATE TABLE sales (
    InvoiceNo VARCHAR(10),
    StockCode VARCHAR(10),
    Description VARCHAR(255),
    Quantity INT,
    InvoiceDate TIMESTAMP,
    UnitPrice DECIMAL(10, 2),
    CustomerID INT,
    Country VARCHAR(50),
    PRIMARY KEY (invoicedate, InvoiceNo)
);

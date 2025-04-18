CREATE TABLE raw.sales (
    InvoiceNo BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    StockCode VARCHAR(10),
    Description VARCHAR(255),
    Quantity INT,
    InvoiceDate TIMESTAMP,
    UnitPrice DECIMAL(10, 2),
    CustomerID INT,
    Country VARCHAR(50)
);

CREATE TABLE stage.sales (
    InvoiceNo BIGINT,
    StockCode VARCHAR(10),
    Description VARCHAR(255),
    Quantity INT,
    InvoiceDate TIMESTAMP,
    UnitPrice DECIMAL(10, 2),
    CustomerID INT,
    Country VARCHAR(50),
    PRIMARY KEY (InvoiceNo)
);

CREATE TABLE dw.fact_sales (
    invoice_number BIGINT,
    stock_code VARCHAR(10),
    sale_description VARCHAR(255),
    quantity INT,
    invoice_date TIMESTAMP,
    unit_price DECIMAL(10, 2),
    customer_sk INT,
    country_id INT NULL,  -- Changed to INT for better foreign key performance
    PRIMARY KEY (invoice_number)
);

CREATE TABLE dw.agg_sales_performance (
  period TIMESTAMP NOT NULL,
  period_type TEXT NOT NULL,
  total_revenue NUMERIC(15,2),
  orders_count INT,
  active_customers INT,
  conversion_rate NUMERIC(5,4),
  avg_customer_value NUMERIC(10,2),
  total_units_sold INT,
  avg_unit_price NUMERIC(10,2),
  active_countries INT,
  domestic_sales NUMERIC(15,2),
  orders_per_hour NUMERIC(6,2),
  repeat_customer_revenue NUMERIC(15,2),
  estimated_gross_profit NUMERIC(15,2)
);


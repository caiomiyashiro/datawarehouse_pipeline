CREATE TABLE dw.dim_customer (
    customer_sk INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY, -- Surrogate key
    customer_id INT,
    customer_name VARCHAR(255),
    customer_email VARCHAR(255),
    country_id INT,
    end_date TIMESTAMP -- SCD2 column: NULL if active
);

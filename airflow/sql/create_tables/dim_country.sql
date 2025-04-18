CREATE TABLE dw.dim_country (
    country_id INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    country_name VARCHAR(50),
    capital VARCHAR(50)
);
ALTER TABLE dw.dim_customer
ADD CONSTRAINT fk_country_id
FOREIGN KEY (country_id)
REFERENCES dw.dim_country(country_id);

ALTER TABLE dw.fact_sales
  ADD CONSTRAINT fk_customer_sk FOREIGN KEY (customer_sk) REFERENCES dw.dim_customer(customer_sk),
  ADD CONSTRAINT fk_country_id FOREIGN KEY (country_id) REFERENCES dw.dim_country(country_id);

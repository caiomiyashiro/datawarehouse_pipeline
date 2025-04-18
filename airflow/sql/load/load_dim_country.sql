INSERT INTO dw.dim_country (country_name)
SELECT DISTINCT rs.country
FROM raw.sales rs
WHERE DATE(rs.invoicedate) = '{{ds}}'::DATE
AND NOT EXISTS (
    SELECT 1
    FROM dw.dim_country dc
    WHERE dc.country_name = rs.Country
);

INSERT INTO dw.dim_country (country_name)
SELECT DISTINCT rs.country_name
FROM stage.sales rs
WHERE DATE(rs.invoice_date) = '{{ds}}'::DATE
AND NOT EXISTS (
    SELECT 1
    FROM dw.dim_country dc
    WHERE dc.country_name = rs.country_name
);

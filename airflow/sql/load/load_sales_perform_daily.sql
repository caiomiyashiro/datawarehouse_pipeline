-- Step 1: Delete existing records for the target date
DELETE FROM dw.agg_sales_performance
WHERE DATE(period) >= '{{ ds }}'::timestamp  -- Start of day
  AND DATE(period) < '{{ ds }}'::timestamp + INTERVAL '1 day';  -- End of day

-- Insert into target table (replace 'sales_performance' with your table name)
INSERT INTO dw.agg_sales_performance (
  period,
  period_type,
  total_revenue,
  orders_count,
  active_customers,
  conversion_rate,
  avg_customer_value,
  total_units_sold,
  avg_unit_price,
  active_countries,
  domestic_sales,
  orders_per_hour,
  repeat_customer_revenue,
  estimated_gross_profit
)
WITH sales_data AS (
  SELECT 
    invoice_number,
    invoice_date,
    DATE_TRUNC('day', invoice_date) AS sale_day,
    DATE_TRUNC('month', invoice_date) AS sale_month,
    quantity,
    unit_price,
    customer_sk,
    country_id,
    quantity * unit_price AS line_total
  FROM dw.fact_sales
  WHERE unit_price > 0 AND quantity > 0 AND DATE(invoice_date) = '{{ ds }}'::DATE
)

-- Core KPIs
SELECT
  sale_day AS period,
  'daily' AS period_type,
  SUM(line_total) AS total_revenue,
  COUNT(DISTINCT invoice_number) AS orders_count,
  COUNT(DISTINCT customer_sk) AS active_customers,
  COUNT(DISTINCT CASE WHEN customer_sk IS NOT NULL THEN customer_sk END) * 1.0 / NULLIF(COUNT(DISTINCT invoice_number), 0) AS conversion_rate,
  SUM(line_total) / NULLIF(COUNT(DISTINCT customer_sk), 0) AS avg_customer_value,
  SUM(quantity) AS total_units_sold,
  SUM(line_total) / NULLIF(SUM(quantity), 0) AS avg_unit_price,
  COUNT(DISTINCT country_id) AS active_countries,
  SUM(line_total) FILTER (WHERE country_id = 20) AS domestic_sales,
  COUNT(DISTINCT invoice_number) * 1.0 / NULLIF(COUNT(DISTINCT DATE_PART('hour', invoice_date)), 0) AS orders_per_hour,
  SUM(line_total) FILTER (WHERE customer_sk IN (
    SELECT customer_sk 
    FROM dw.fact_sales 
    WHERE DATE(invoice_date) <= '{{ ds }}'::DATE  -- Historical filter
    GROUP BY customer_sk 
    HAVING COUNT(DISTINCT invoice_number) > 1
  )) AS repeat_customer_revenue,
  SUM(line_total * 0.3) AS estimated_gross_profit
FROM sales_data
GROUP BY sale_day;

 
-- 1. **Revenue Metrics**  
--    - Total revenue (daily/monthly)[1][5]  
--    - Average unit price[1][3]  
--    - Estimated gross profit[5]  

-- 2. **Customer Behavior**  
--    - Conversion rate (leads to orders)[2][3]  
--    - Average customer value[5]  
--    - Repeat customer revenue[5]  
--    - Active customers[4]  

-- 3. **Operational Efficiency**  
--    - Orders per hour (sales velocity)[4]  
--    - Units sold[1]  
--    - Order count[5]  

-- 4. **Geographic Performance**  
--    - Domestic vs international sales[7]  
--    - Active country count  

-- 5. **Trend Analysis**  
--    - Daily vs monthly performance[1][5]  
--    - Cohort retention tracking[5]  

-- **Visualization Recommendations:**  
-- - **Time Series:** Revenue/orders over time with moving averages  
-- - **Bar Charts:** Top countries, best-selling products (via stock_code)  
-- - **Gauge Widgets:** Conversion rate vs industry benchmarks[2]  
-- - **Heatmaps:** Hourly/daily sales patterns  
-- - **Cohort Tables:** Repeat customer retention rates  
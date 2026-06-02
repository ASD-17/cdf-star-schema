-- ── Query 1: Total Sales by Product and Month ─────────────────────────────
SELECT
    d.year,
    d.month_name,
    p.description                           AS product,
    SUM(f.quantity)                         AS total_units_sold,
    ROUND(SUM(f.total_amount), 2)           AS total_revenue_gbp
FROM fact_sales f
JOIN dim_date    d ON f.date_key    = d.date_key
JOIN dim_product p ON f.product_key = p.product_key
GROUP BY d.year, d.month, d.month_name, p.description
ORDER BY d.year, d.month, total_revenue_gbp DESC;

-- ── Query 2: Top 10 Customers by Revenue ─────────────────────────────────
SELECT
    c.customer_id,
    c.country,
    COUNT(DISTINCT i.invoice_no)            AS total_orders,
    SUM(f.quantity)                         AS total_units,
    ROUND(SUM(f.total_amount), 2)           AS total_spent_gbp
FROM fact_sales f
JOIN dim_customer c ON f.customer_key = c.customer_key
JOIN dim_invoice  i ON f.invoice_key  = i.invoice_key
GROUP BY c.customer_id, c.country
ORDER BY total_spent_gbp DESC
LIMIT 10;

-- ── Query 3: Monthly Revenue Trend ───────────────────────────────────────
SELECT
    d.year,
    d.month,
    d.month_name,
    ROUND(SUM(f.total_amount), 2)           AS monthly_revenue_gbp,
    COUNT(DISTINCT i.invoice_no)            AS total_invoices
FROM fact_sales f
JOIN dim_date    d ON f.date_key   = d.date_key
JOIN dim_invoice i ON f.invoice_key = i.invoice_key
GROUP BY d.year, d.month, d.month_name
ORDER BY d.year, d.month;

-- ── Query 4: Revenue by Country ───────────────────────────────────────────
SELECT
    c.country,
    COUNT(DISTINCT c.customer_id)           AS unique_customers,
    ROUND(SUM(f.total_amount), 2)           AS total_revenue_gbp
FROM fact_sales f
JOIN dim_customer c ON f.customer_key = c.customer_key
GROUP BY c.country
ORDER BY total_revenue_gbp DESC;
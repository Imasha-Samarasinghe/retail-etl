-- Q1: Top 10 products by revenue
SELECT p.stock_code, p.description, SUM(l.line_total) AS revenue, SUM(l.quantity) AS units
FROM invoice_lines l
JOIN invoices i ON i.invoice_no = l.invoice_no
JOIN products p ON p.stock_code = l.stock_code
WHERE NOT i.is_cancellation
GROUP BY p.stock_code, p.description
ORDER BY revenue DESC
LIMIT 10;

-- Q2: Monthly revenue with month-over-month growth
WITH monthly AS (
    SELECT date_trunc('month', i.invoice_date) AS month, SUM(l.line_total) AS revenue
    FROM invoices i
    JOIN invoice_lines l ON l.invoice_no = i.invoice_no
    WHERE NOT i.is_cancellation
    GROUP BY 1
)
SELECT month::date, ROUND(revenue, 2) AS revenue,
       ROUND(100.0 * (revenue - LAG(revenue) OVER (ORDER BY month))
             / NULLIF(LAG(revenue) OVER (ORDER BY month), 0), 1) AS mom_growth_pct
FROM monthly
ORDER BY month;

-- Q3: Average order value by country for one month
SELECT i.country,
       COUNT(DISTINCT i.invoice_no) AS orders,
       ROUND(SUM(l.line_total) / COUNT(DISTINCT i.invoice_no), 2) AS avg_order_value
FROM invoices i
JOIN invoice_lines l ON l.invoice_no = i.invoice_no
WHERE NOT i.is_cancellation
  AND i.invoice_date >= '2011-11-01' AND i.invoice_date < '2011-12-01'
GROUP BY i.country
ORDER BY avg_order_value DESC;

-- Q4: One customer's order history
SELECT i.invoice_no, i.invoice_date, ROUND(SUM(l.line_total), 2) AS order_total
FROM invoices i
JOIN invoice_lines l ON l.invoice_no = i.invoice_no
WHERE i.customer_id = 14911
GROUP BY i.invoice_no, i.invoice_date
ORDER BY i.invoice_date;
CREATE MATERIALIZED VIEW IF NOT EXISTS mv_product_revenue AS
SELECT l.stock_code, SUM(l.line_total) AS revenue, SUM(l.quantity) AS units
FROM invoice_lines l
JOIN invoices i ON i.invoice_no = l.invoice_no
WHERE NOT i.is_cancellation
GROUP BY l.stock_code;

CREATE INDEX IF NOT EXISTS idx_mv_revenue ON mv_product_revenue (revenue DESC);
ANALYZE mv_product_revenue;
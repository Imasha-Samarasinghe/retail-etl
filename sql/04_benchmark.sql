ANALYZE;

-- Q1 (full aggregation: expect NO index benefit)
EXPLAIN (ANALYZE, BUFFERS)
SELECT p.stock_code, SUM(l.line_total) AS revenue
FROM invoice_lines l
JOIN invoices i ON i.invoice_no = l.invoice_no
JOIN products p ON p.stock_code = l.stock_code
WHERE NOT i.is_cancellation
GROUP BY p.stock_code ORDER BY revenue DESC LIMIT 10;

-- Q3 (one month, about 4% of rows: expect a benefit from idx_invoices_date)
EXPLAIN (ANALYZE, BUFFERS)
SELECT i.country, COUNT(DISTINCT i.invoice_no), SUM(l.line_total)
FROM invoices i
JOIN invoice_lines l ON l.invoice_no = i.invoice_no
WHERE NOT i.is_cancellation
  AND i.invoice_date >= '2011-11-01' AND i.invoice_date < '2011-12-01'
GROUP BY i.country;

-- Q4 (single customer: expect a big benefit from idx_invoices_customer)
EXPLAIN (ANALYZE, BUFFERS)
SELECT i.invoice_no, SUM(l.line_total)
FROM invoices i
JOIN invoice_lines l ON l.invoice_no = i.invoice_no
WHERE i.customer_id = 14911
GROUP BY i.invoice_no;
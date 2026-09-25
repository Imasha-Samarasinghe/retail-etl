SET random_page_cost = 1.1;
EXPLAIN (ANALYZE, BUFFERS)
SELECT i.invoice_no, SUM(l.line_total)
FROM invoices i JOIN invoice_lines l ON l.invoice_no = i.invoice_no
WHERE i.customer_id = 14911
GROUP BY i.invoice_no;
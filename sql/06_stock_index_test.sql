DROP INDEX IF EXISTS idx_lines_stock;
EXPLAIN (ANALYZE, BUFFERS)
SELECT COUNT(*), SUM(line_total) FROM invoice_lines WHERE stock_code = '85123A';

CREATE INDEX idx_lines_stock ON invoice_lines (stock_code);
ANALYZE invoice_lines;
EXPLAIN (ANALYZE, BUFFERS)
SELECT COUNT(*), SUM(line_total) FROM invoice_lines WHERE stock_code = '85123A';
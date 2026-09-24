-- Postgres does NOT auto-index foreign key columns, only primary keys
CREATE INDEX idx_invoices_date     ON invoices (invoice_date);
CREATE INDEX idx_invoices_customer ON invoices (customer_id);
CREATE INDEX idx_lines_stock       ON invoice_lines (stock_code);
ANALYZE;
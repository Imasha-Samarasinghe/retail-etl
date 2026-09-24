CREATE TABLE customers (
    customer_id INTEGER PRIMARY KEY
);

CREATE TABLE products (
    stock_code  TEXT PRIMARY KEY,
    description TEXT
);

CREATE TABLE invoices (
    invoice_no      TEXT PRIMARY KEY,
    customer_id     INTEGER REFERENCES customers(customer_id),  -- NULL = guest checkout
    invoice_date    TIMESTAMP NOT NULL,
    country         TEXT NOT NULL,
    is_cancellation BOOLEAN NOT NULL DEFAULT FALSE
);

CREATE TABLE invoice_lines (
    invoice_no TEXT    NOT NULL REFERENCES invoices(invoice_no),
    line_no    INTEGER NOT NULL,
    stock_code TEXT    NOT NULL REFERENCES products(stock_code),
    quantity   INTEGER NOT NULL CHECK (quantity <> 0),
    unit_price NUMERIC(10,2) NOT NULL CHECK (unit_price > 0),
    line_total NUMERIC(12,2) NOT NULL,
    PRIMARY KEY (invoice_no, line_no)
);

CREATE TABLE etl_runs (
    run_id        SERIAL PRIMARY KEY,
    started_at    TIMESTAMP NOT NULL,
    finished_at   TIMESTAMP,
    rows_read     INTEGER,
    rows_rejected INTEGER,
    rows_loaded   INTEGER,
    status        TEXT
);
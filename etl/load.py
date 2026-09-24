import io
import logging
import psycopg2
from config.settings import DB

log = logging.getLogger(__name__)

STG_COLS = ["invoice_no", "line_no", "stock_code", "description", "quantity",
            "invoice_date", "unit_price", "line_total", "customer_id",
            "country", "is_cancellation"]


def get_conn():
    return psycopg2.connect(**DB)


def _copy(cur, df, table, cols):
    buf = io.StringIO()
    df[cols].to_csv(buf, index=False, header=False, na_rep="\\N")
    buf.seek(0)
    cur.copy_expert(
        f"COPY {table} ({','.join(cols)}) FROM STDIN WITH (FORMAT csv, NULL '\\N')", buf)


def start_run() -> int:
    conn = get_conn()
    try:
        with conn, conn.cursor() as cur:
            cur.execute("INSERT INTO etl_runs (started_at, status) "
                        "VALUES (now(), 'running') RETURNING run_id")
            return cur.fetchone()[0]
    finally:
        conn.close()


def finish_run(run_id, read, rejected, loaded, status):
    conn = get_conn()
    try:
        with conn, conn.cursor() as cur:
            cur.execute("""UPDATE etl_runs SET finished_at = now(), rows_read = %s,
                           rows_rejected = %s, rows_loaded = %s, status = %s
                           WHERE run_id = %s""",
                        (read, rejected, loaded, status, run_id))
    finally:
        conn.close()


def load(clean) -> int:
    """Bulk-load via COPY into a staging table, then upsert into the real tables
    in ONE transaction. Safe to re-run: existing rows are skipped."""
    clean = clean.copy()
    clean["quantity"] = clean["quantity"].astype(int)
    clean["line_no"] = clean.groupby("invoice_no").cumcount() + 1

    conn = get_conn()
    try:
        with conn, conn.cursor() as cur:
            cur.execute("""CREATE TEMP TABLE stg (
                invoice_no TEXT, line_no INT, stock_code TEXT, description TEXT,
                quantity INT, invoice_date TIMESTAMP, unit_price NUMERIC(10,2),
                line_total NUMERIC(12,2), customer_id INT, country TEXT,
                is_cancellation BOOLEAN) ON COMMIT DROP""")
            _copy(cur, clean, "stg", STG_COLS)

            cur.execute("""INSERT INTO customers (customer_id)
                           SELECT DISTINCT customer_id FROM stg
                           WHERE customer_id IS NOT NULL
                           ON CONFLICT DO NOTHING""")
            cur.execute("""INSERT INTO products (stock_code, description)
                           SELECT stock_code, MAX(description) FROM stg
                           GROUP BY stock_code ON CONFLICT DO NOTHING""")
            cur.execute("""INSERT INTO invoices
                               (invoice_no, customer_id, invoice_date, country, is_cancellation)
                           SELECT invoice_no, MAX(customer_id), MIN(invoice_date),
                                  MAX(country), BOOL_OR(is_cancellation)
                           FROM stg GROUP BY invoice_no ON CONFLICT DO NOTHING""")
            cur.execute("""INSERT INTO invoice_lines
                               (invoice_no, line_no, stock_code, quantity, unit_price, line_total)
                           SELECT invoice_no, line_no, stock_code, quantity, unit_price, line_total
                           FROM stg ON CONFLICT DO NOTHING""")
            inserted = cur.rowcount
    finally:
        conn.close()
    log.info("Inserted %s new invoice lines", inserted)
    return inserted

import pandas as pd

NON_PRODUCT = {"POST", "D", "M", "BANK CHARGES", "DOT", "CRUK", "PADS", "AMAZONFEE",
               "S", "B", "ADJUST", "C2", "TEST001"}
KEY_COLS = ["invoice_no", "stock_code", "quantity",
            "invoice_date", "unit_price", "customer_id"]


def validate(df: pd.DataFrame):
    rules = [
        ("duplicate",            df.duplicated(subset=KEY_COLS, keep="first")),
        ("missing_invoice_no",   df["invoice_no"].isna()),
        ("missing_invoice_date", df["invoice_date"].isna()),
        ("missing_stock_code",   df["stock_code"].isna()),
        ("non_product_code",     df["stock_code"].isin(NON_PRODUCT)),
        ("bad_quantity",         df["quantity"].isna() | (df["quantity"] == 0)
         | ((df["quantity"] < 0) & ~df["is_cancellation"])),
        ("bad_price",            df["unit_price"].isna() | (
            df["unit_price"] <= 0)),
    ]
    reason = pd.Series("", index=df.index)
    bad = pd.Series(False, index=df.index)
    for name, mask in rules:
        reason[mask & ~bad] = name      # first matching rule wins
        bad |= mask
    clean = df[~bad].copy()
    rejects = df[bad].assign(reject_reason=reason[bad])
    return clean, rejects

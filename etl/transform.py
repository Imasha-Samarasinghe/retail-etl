import pandas as pd

COLS = {
    "Invoice": "invoice_no", "StockCode": "stock_code", "Description": "description",
    "Quantity": "quantity", "InvoiceDate": "invoice_date", "Price": "unit_price",
    "Customer ID": "customer_id", "Country": "country",
}


def standardize(df: pd.DataFrame) -> pd.DataFrame:
    df = df.rename(columns=COLS)
    for c in ["invoice_no", "stock_code", "description", "country"]:
        # empty strings become real nulls
        df[c] = df[c].str.strip().replace("", pd.NA)
    df["stock_code"] = df["stock_code"].str.upper()
    df["description"] = df["description"].str.upper().str.replace(r"\s+",
                                                                  " ", regex=True)
    df["country"] = df["country"].str.title()
    df["quantity"] = pd.to_numeric(df["quantity"], errors="coerce")
    df["unit_price"] = pd.to_numeric(df["unit_price"], errors="coerce")
    df["invoice_date"] = pd.to_datetime(df["invoice_date"], errors="coerce")
    df["customer_id"] = pd.to_numeric(
        df["customer_id"], errors="coerce").astype("Int64")
    df["is_cancellation"] = df["invoice_no"].str.startswith("C", na=False)
    df["line_total"] = (df["quantity"] * df["unit_price"]).round(2)

    # One canonical description per stock_code: the most frequent one
    mode_desc = (df.dropna(subset=["description"])
                   .groupby("stock_code")["description"]
                   .agg(lambda x: x.mode().iloc[0]))
    df["description"] = df["stock_code"].map(
        mode_desc).fillna(df["description"])
    return df

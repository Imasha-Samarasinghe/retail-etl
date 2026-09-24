import pandas as pd
from etl.extract import extract
from etl.transform import standardize
from etl.validate import KEY_COLS

raw = extract()
df = standardize(raw.copy())

print("shape:", raw.shape)
print("\nnull % per column:\n", (raw.isna().mean() * 100).round(2))
print("\nexact duplicate rows:", raw.duplicated().sum())
print("dupes with customer_id in key:", df.duplicated(subset=KEY_COLS).sum())
print("dupes without customer_id    :", df.duplicated(
    subset=[c for c in KEY_COLS if c != "customer_id"]).sum())

print("\ndate range:", df.invoice_date.min(), "->", df.invoice_date.max())
print("unparseable dates:", df.invoice_date.isna().sum())

print("\ncancellation invoices:", df.is_cancellation.sum())
print("qty <= 0:", (df.quantity <= 0).sum(),
      "| non-cancellation:", ((df.quantity <= 0) & ~df.is_cancellation).sum())
print("price <= 0:", (df.unit_price <= 0).sum())

print("\nnon-standard stock codes:")
print(df.loc[~df.stock_code.str.match(
    r"^\d{5}", na=False), "stock_code"].value_counts().head(20))

print("\ntop countries:\n", df.country.value_counts().head(10))
print("distinct countries:", df.country.nunique())

print("\nquantity:\n", df.quantity.describe())
print("\nprice:\n", df.unit_price.describe())

print("\nstock codes with >1 raw description:",
      (raw.groupby("StockCode")["Description"].nunique() > 1).sum())
print("invoices with >1 country :", (df.groupby(
    "invoice_no").country.nunique() > 1).sum())
print("invoices with >1 customer:", (df.groupby(
    "invoice_no").customer_id.nunique() > 1).sum())
print("invoices with >1 date    :", (df.groupby(
    "invoice_no").invoice_date.nunique() > 1).sum())

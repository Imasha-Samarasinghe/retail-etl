import pandas as pd
from etl.transform import standardize
from etl.validate import validate

COLS = ["Invoice", "StockCode", "Description", "Quantity",
        "InvoiceDate", "Price", "Customer ID", "Country"]


def run(rows):
    return validate(standardize(pd.DataFrame(rows, columns=COLS)))


def test_cancellation_kept_and_normalized():
    clean, rej = run([["C1001", "85123a", " heart  holder ", "-2",
                       "2010-01-01 10:00:00", "2.5", "12345.0", " united kingdom "]])
    assert len(clean) == 1 and len(rej) == 0
    row = clean.iloc[0]
    assert row.is_cancellation
    assert row.country == "United Kingdom"
    assert row.description == "HEART HOLDER"
    assert row.stock_code == "85123A"


def test_duplicate_rejected():
    r = ["1001", "85123A", "X", "1",
         "2010-01-01 10:00:00", "2.5", "12345", "France"]
    clean, rej = run([r, r])
    assert len(clean) == 1
    assert rej.iloc[0].reject_reason == "duplicate"


def test_bad_price_rejected():
    _, rej = run(
        [["1001", "85123A", "X", "1", "2010-01-01 10:00:00", "0", "12345", "France"]])
    assert rej.iloc[0].reject_reason == "bad_price"


def test_non_product_code_rejected():
    _, rej = run([["1001", "POST", "POSTAGE", "1",
                 "2010-01-01 10:00:00", "18", "12345", "France"]])
    assert rej.iloc[0].reject_reason == "non_product_code"


def test_guest_checkout_kept():
    clean, _ = run(
        [["1001", "85123A", "X", "1", "2010-01-01 10:00:00", "2.5", None, "France"]])
    assert len(clean) == 1 and pd.isna(clean.iloc[0].customer_id)

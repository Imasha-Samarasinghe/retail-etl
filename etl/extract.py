import pandas as pd
from config.settings import RAW_FILE


def extract(sample=None):
    # Read everything as strings so cleaning is explicit and nothing is silently coerced
    return pd.read_csv(RAW_FILE, dtype=str, nrows=sample)

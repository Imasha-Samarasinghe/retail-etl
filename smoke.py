from etl.extract import extract
from etl.transform import standardize
from etl.validate import validate

df = standardize(extract(sample=50000))
clean, rej = validate(df)
print("read:", len(df), "clean:", len(clean), "rejected:", len(rej))
print(rej["reject_reason"].value_counts())

# Check for invoice_no collisions across the two years — critical before we design the PK
collision_check = df.groupby("invoice_no")["invoice_date"].apply(
    lambda x: x.dt.year.nunique())
print("invoice_no reused across different years:", (collision_check > 1).sum())

import pandas as pd

# نقرأ appVersion كنص، حتى لا يتحول "15.050" إلى الرقم 15.05
df = pd.read_csv("data/reviews_raw.csv", dtype={"appVersion": str})

# المراجعات الفارغة نجعلها نصًا فارغًا بدل NaN
df["content"] = df["content"].fillna("")
df["word_count"] = df["content"].str.split().str.len()

print("=== Overview ===")
print("Total reviews:", len(df))
print("Date range:", df["at"].min(), "->", df["at"].max())
print("Average stars:", round(df["score"].mean(), 2))

print("\n=== Stars distribution (%) ===")
print(df["score"].value_counts(normalize=True).sort_index().mul(100).round(1))

print("\n=== Review length ===")
print("Empty (0 words):     ", (df["word_count"] == 0).sum())
print("Short (1-3 words):   ", df["word_count"].between(1, 3).sum())
print("Useful (4+ words):   ", (df["word_count"] >= 4).sum())

print("\n=== App versions ===")
print("Missing appVersion:", df["appVersion"].isna().sum())
print(df["appVersion"].value_counts().head(5))
import pandas as pd

LABELS_PATH = "data/labeling_blind.csv"
MODEL_PATH = "data/reviews_classified.csv"


def load_labels(path):
    """Excel أو WPS قد يحفظ الملف بفاصلة , أو ; وبترميز مختلف، فنجرّب الحالتين."""
    for enc in ["utf-8-sig", "cp1254"]:
        try:
            return pd.read_csv(path, sep=None, engine="python", encoding=enc)
        except UnicodeDecodeError:
            continue
    raise ValueError("Could not read the labels file")


# 1) نقرأ تصنيفك وننظفه (نحذف المسافات، ونحوّل إلى حروف صغيرة)
labels = load_labels(LABELS_PATH)
for col in ["my_category", "my_sentiment"]:
    labels[col] = labels[col].astype(str).str.strip().str.lower()

print("=== Sanity check ===")
print("Rows:", len(labels))
print("Columns:", list(labels.columns))
print("My categories:", labels["my_category"].value_counts().to_dict())
print("My sentiments:", labels["my_sentiment"].value_counts().to_dict())

# 2) ندمج مع تصنيف النموذج
model = pd.read_csv(MODEL_PATH)[["reviewId", "category", "sentiment"]]
df = labels.merge(model, on="reviewId", how="left")
print("Matched with model:", df["category"].notna().sum(), "/", len(df))

# 3) الدقة (accuracy): كم مرة اتفقتِ أنتِ والنموذج؟
cat_ok = df["my_category"] == df["category"]
sent_ok = df["my_sentiment"] == df["sentiment"]
print("\n=== Accuracy (model vs. you) ===")
print(f"Category:  {cat_ok.mean():.0%}  ({cat_ok.sum()}/{len(df)})")
print(f"Sentiment: {sent_ok.mean():.0%}  ({sent_ok.sum()}/{len(df)})")
print(f"Both:      {(cat_ok & sent_ok).mean():.0%}  ({(cat_ok & sent_ok).sum()}/{len(df)})")

# 4) Confusion matrix: الصفوف تصنيفك، والأعمدة تصنيف النموذج
print("\n=== Category confusion matrix (rows = you, columns = model) ===")
print(pd.crosstab(df["my_category"], df["category"]))

# 5) المراجعات التي اختلفنا فيها
print("\n=== Category disagreements ===")
for i, r in df[~cat_ok].iterrows():
    print(f"\n[#{i + 1}] you={r['my_category']} | model={r['category']}")
    print("    ", str(r["content"])[:120])
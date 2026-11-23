import pandas as pd

df = pd.read_csv("data/reviews_classified.csv", dtype={"appVersion": str})

# عيّنة عشوائية ثابتة: random_state=42 يعطي نفس الـ 50 في كل مرة
sample = df.sample(n=50, random_state=42)

# ملف أعمى: النص فقط، بدون تصنيف النموذج
blind = sample[["reviewId", "content"]].copy()
blind["my_category"] = ""
blind["my_sentiment"] = ""

# utf-8-sig حتى يفتح Excel الحروف بشكل صحيح
blind.to_csv("data/labeling_blind.csv", index=False, encoding="utf-8-sig")
print("Saved", len(blind), "reviews to data/labeling_blind.csv")
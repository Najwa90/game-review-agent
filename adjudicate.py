import pandas as pd

LABELS_PATH = "data/labeling_blind.csv"
MODEL_PATH = "data/reviews_classified.csv"
GOLD_PATH = "data/labeling_gold.csv"

# قرارات المراجعة (Adjudication): رقم المراجعة -> التصنيف النهائي
CATEGORY_OVERRIDES = {
    6: "bug",           # لا تُحمَّل وتطرد اللاعب = شيء لا يعمل
    10: "bug",          # glitch = خطأ تقني
    20: "praise",       # مدح بدون شكوى
    27: "other",        # عن التقييمات، لا عن الإعلانات
    31: "monetization", # سخرية: "رائعة إذا دفعت"
    39: "bug",          # لا يستطيع تسجيل الدخول
    40: "other",        # لا يذكر المباريات أو الفرق
}
AMBIGUOUS = {19, 26, 32, 49}  # التصنيفان مقبولان

labels = pd.read_csv(LABELS_PATH, encoding="utf-8-sig")
model = pd.read_csv(MODEL_PATH)[["reviewId", "category", "sentiment"]]
df = labels.merge(model, on="reviewId", how="left")
df["n"] = range(1, len(df) + 1)  # رقم المراجعة من 1 إلى 50

# التصنيف النهائي = تصنيفك، مع تطبيق قرارات المراجعة
df["gold_category"] = df["my_category"]
for n, cat in CATEGORY_OVERRIDES.items():
    df.loc[df["n"] == n, "gold_category"] = cat
df["ambiguous"] = df["n"].isin(AMBIGUOUS)

df.to_csv(GOLD_PATH, index=False, encoding="utf-8-sig")

# الدقة على المراجعات الواضحة فقط
clear = df[~df["ambiguous"]]
correct = (clear["gold_category"] == clear["category"]).sum()
print("=== Final category accuracy ===")
print(f"Before adjudication (vs. your raw labels): 39/50 = 78%")
print(f"After adjudication (clear reviews only):   {correct}/{len(clear)} = {correct / len(clear):.0%}")
print(f"Ambiguous reviews (both labels acceptable): {len(AMBIGUOUS)}/50 = {len(AMBIGUOUS) / 50:.0%}")

# اختلافات المشاعر: لم نرها بعد
print("\n=== Sentiment disagreements ===")
diff = df[df["my_sentiment"] != df["sentiment"]]
for _, r in diff.iterrows():
    print(f"\n[#{r['n']}] you={r['my_sentiment']} | model={r['sentiment']}")
    print("    ", str(r["content"])[:120])
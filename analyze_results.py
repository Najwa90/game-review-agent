import pandas as pd

pd.set_option("display.width", 120)
df = pd.read_csv("data/reviews_classified.csv", dtype={"appVersion": str})

# سؤال 1: ما أكثر المواضيع التي يتكلم عنها اللاعبون؟
print("=== 1) Categories ===")
counts = df["category"].value_counts()
pct = df["category"].value_counts(normalize=True).mul(100).round(1)
print(pd.DataFrame({"count": counts, "pct": pct}))

# سؤال 2: ما المشاعر العامة؟
print("\n=== 2) Sentiment ===")
print(df["sentiment"].value_counts())

# سؤال 3: أي موضوع يرتبط بأقل تقييم؟
print("\n=== 3) Average stars per category ===")
print(df.groupby("category")["score"].agg(["count", "mean"]).round(2).sort_values("mean"))

# سؤال 4: هل تغيّرت المواضيع بين الإصدارات؟
print("\n=== 4) Category share by app version (%) ===")
top_versions = df["appVersion"].value_counts().head(4).index
sub = df[df["appVersion"].isin(top_versions)]
print(pd.crosstab(sub["appVersion"], sub["category"], normalize="index").mul(100).round(0))

# سؤال 5: أي الشكاوى يتفق معها لاعبون كثيرون؟ (أكثر 👍)
print("\n=== 5) Most-liked complaints ===")
complaints = df[df["category"].isin(["bug", "performance", "monetization"])]
top = complaints.sort_values("thumbsUpCount", ascending=False).head(5)
for _, r in top.iterrows():
    print(f"\n[{r['category']}] stars={r['score']} likes={r['thumbsUpCount']}")
    print("   ", r["summary"])
import pandas as pd

df = pd.read_csv("data/reviews_classified.csv", dtype={"appVersion": str})
other = df[df["category"] == "other"]

print("Number of 'other' reviews:", len(other))

for i, (_, r) in enumerate(other.iterrows(), start=1):
    print(f"\n[{i}] stars={r['score']} | {r['sentiment']}")
    print("   Summary:", r["summary"])
    print("   Text:   ", r["content"][:200])
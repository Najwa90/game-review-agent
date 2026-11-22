import time
import pandas as pd
from classifier import classify_review

INPUT_PATH = "data/reviews_raw.csv"
OUTPUT_PATH = "data/reviews_classified.csv"
MIN_WORDS = 4
LIMIT = None
SLEEP_SECONDS = 1


def classify_with_retry(text, attempts=4, base_wait=10):
    """نحاول حتى 4 مرات، وننتظر وقتًا أطول بعد كل فشل: 10، ثم 20، ثم 40 ثانية."""
    for attempt in range(1, attempts + 1):
        try:
            return classify_review(text)
        except Exception as e:
            print(f"   attempt {attempt} failed: {type(e).__name__}: {str(e)[:100]}")
            if attempt < attempts:
                time.sleep(base_wait * 2 ** (attempt - 1))
    return {"category": None, "sentiment": None, "summary": None, "valid": False}


if __name__ == "__main__":
    df = pd.read_csv(INPUT_PATH, dtype={"appVersion": str})
    df["content"] = df["content"].fillna("")
    df["word_count"] = df["content"].str.split().str.len()
    useful = df[df["word_count"] >= MIN_WORDS].copy()

    if LIMIT:
        useful = useful.head(LIMIT)
    print("Reviews to classify:", len(useful))

    results = []
    start = time.time()
    for i, (_, row) in enumerate(useful.iterrows(), start=1):
        result = classify_with_retry(row["content"])
        result["reviewId"] = row["reviewId"]
        results.append(result)
        print(f"[{i}/{len(useful)}] {result.get('category')} | {result.get('sentiment')}")
        time.sleep(SLEEP_SECONDS)

    out = useful.merge(pd.DataFrame(results), on="reviewId", how="left")
    out.to_csv(OUTPUT_PATH, index=False, encoding="utf-8")

    elapsed = time.time() - start
    print("\nSaved to:", OUTPUT_PATH)
    print(f"Time: {elapsed:.1f} seconds")
    print("Valid:", int(out["valid"].sum()), "/", len(out))
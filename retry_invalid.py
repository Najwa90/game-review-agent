import time
import pandas as pd
from classify_batch import classify_with_retry, SLEEP_SECONDS, OUTPUT_PATH

# 1) نقرأ النتائج السابقة
df = pd.read_csv(OUTPUT_PATH, dtype={"appVersion": str})

# 2) نجد المراجعات غير الصحيحة
invalid_mask = df["valid"] != True
print("Invalid before:", int(invalid_mask.sum()))

# 3) نعيد تصنيفها وحدها
for idx in df[invalid_mask].index:
    result = classify_with_retry(df.at[idx, "content"])
    for key in ["category", "sentiment", "summary", "valid"]:
        df.at[idx, key] = result.get(key)
    print(f"[row {idx}] {result.get('category')} | {result.get('sentiment')}")
    time.sleep(SLEEP_SECONDS)

# 4) نحفظ فوق نفس الملف
df.to_csv(OUTPUT_PATH, index=False, encoding="utf-8")
print("\nValid after:", int((df["valid"] == True).sum()), "/", len(df))
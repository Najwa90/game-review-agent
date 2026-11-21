import os
import pandas as pd
from google_play_scraper import reviews, Sort

APP_ID = "com.critical.strike2"
N_REVIEWS = 500
OUTPUT_PATH = "data/reviews_raw.csv"

# الأعمدة التي نحتاجها فقط (بدون userName وuserImage للخصوصية)
COLUMNS = ["reviewId", "content", "score", "thumbsUpCount", "appVersion", "at"]

result, _ = reviews(
    APP_ID,
    lang="en",
    country="us",
    sort=Sort.NEWEST,
    count=N_REVIEWS,
)
print("Fetched:", len(result), "reviews")

df = pd.DataFrame(result)[COLUMNS]

os.makedirs("data", exist_ok=True)
df.to_csv(OUTPUT_PATH, index=False, encoding="utf-8")
print("Saved to:", OUTPUT_PATH)
print(df.head())
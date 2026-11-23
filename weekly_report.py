import os
import json
import time
from datetime import timedelta
import pandas as pd
from google.genai import types
from classifier import client, MODEL

RAW_PATH = "data/reviews_raw.csv"
CLASSIFIED_PATH = "data/reviews_classified.csv"
REPORT_DIR = "reports"
COMPLAINTS = ["bug", "performance", "monetization", "matchmaking", "misleading_ads"]

# نماذج الملخص بالترتيب: إذا فشل الأول، نجرّب الثاني
SUMMARY_MODELS = [MODEL, "gemini-3.5-flash"]

# 1) نقرأ البيانات، ونحدد الأسبوعين
raw = pd.read_csv(RAW_PATH, dtype={"appVersion": str}, parse_dates=["at"])
cls = pd.read_csv(CLASSIFIED_PATH, dtype={"appVersion": str}, parse_dates=["at"])

end = raw["at"].max()
start_this = end - timedelta(days=7)
start_prev = end - timedelta(days=14)


def in_period(df, start, stop):
    return df[(df["at"] > start) & (df["at"] <= stop)]


raw_this, raw_prev = in_period(raw, start_this, end), in_period(raw, start_prev, start_this)
cls_this, cls_prev = in_period(cls, start_this, end), in_period(cls, start_prev, start_this)


# 2) الأرقام الأساسية (KPIs): يحسبها الكود، لا الـ LLM
def kpis(raw_df):
    return {
        "reviews": len(raw_df),
        "avg_stars": round(raw_df["score"].mean(), 2),
        "one_star_pct": round((raw_df["score"] == 1).mean() * 100, 1),
    }


k_this, k_prev = kpis(raw_this), kpis(raw_prev)

cat = pd.DataFrame({
    "this_week": cls_this["category"].value_counts(),
    "last_week": cls_prev["category"].value_counts(),
}).fillna(0).astype(int)
cat["change"] = cat["this_week"] - cat["last_week"]
cat = cat.sort_values("this_week", ascending=False)

top = (cls_this[cls_this["category"].isin(COMPLAINTS)]
       .sort_values("thumbsUpCount", ascending=False).head(3))

# 3) الـ LLM يكتب الملخص والتوصيات من الأرقام فقط
stats = {
    "this_week": k_this,
    "last_week": k_prev,
    "categories": cat.to_dict(orient="index"),
    "top_complaints": top[["category", "score", "thumbsUpCount", "summary"]].to_dict(orient="records"),
}

prompt = f"""You are a product analyst at a mobile game studio.
Below are this week's player review statistics (JSON), compared with last week.

Write:
1) Key insights: 3 short bullet points.
2) Recommendations: 3 short, concrete bullet points, each for the dev, product, or marketing team.

Rules:
- Use ONLY numbers that appear in the JSON. Never invent numbers.
- For counts under 5, call them "signals", not "trends".
- Plain English, markdown bullets, no headers.

JSON:
{json.dumps(stats, indent=2, default=str)}
"""


def write_summary(prompt):
    """نجرّب كل نموذج حتى 2 مرات. نُرجع (النص، اسم النموذج) أو (None, None)."""
    for model_name in SUMMARY_MODELS:
        for attempt in range(1, 3):
            try:
                response = client.models.generate_content(
                    model=model_name,
                    contents=prompt,
                    config=types.GenerateContentConfig(temperature=0.2),
                )
                return response.text.strip(), model_name
            except Exception as e:
                print(f"   {model_name} attempt {attempt} failed: {type(e).__name__}: {str(e)[:120]}")
                if attempt < 2:
                    time.sleep(10)
    return None, None


ai_text, used_model = write_summary(prompt)
if ai_text is None:
    ai_text = "_AI summary unavailable (all models failed). Numbers above are still valid._"
    used_model = "none"

# 4) نبني التقرير بصيغة Markdown
L = []
L.append("# Weekly Player Review Report: Critical Strike")
L.append(f"**Period:** {start_this:%Y-%m-%d} to {end:%Y-%m-%d} (vs. previous 7 days)\n")

L.append("## Key numbers")
L.append("| Metric | This week | Last week |")
L.append("|---|---|---|")
L.append(f"| Reviews | {k_this['reviews']} | {k_prev['reviews']} |")
L.append(f"| Average stars | {k_this['avg_stars']} | {k_prev['avg_stars']} |")
L.append(f"| 1-star reviews | {k_this['one_star_pct']}% | {k_prev['one_star_pct']}% |\n")

L.append("## Topics (reviews with 4+ words)")
L.append("| Category | This week | Last week | Change |")
L.append("|---|---|---|---|")
for name, r in cat.iterrows():
    L.append(f"| {name} | {r['this_week']} | {r['last_week']} | {r['change']:+d} |")
L.append("")

L.append("## Most-liked complaints this week")
for _, r in top.iterrows():
    L.append(f"- **{r['category']}** · {r['score']} stars · {r['thumbsUpCount']} likes: {r['summary']}")
L.append("")

L.append("## AI summary and recommendations")
L.append(f"_Written by `{used_model}` from the numbers above only._\n")
L.append(ai_text + "\n")

L.append("## Method")
L.append(f"- Source: Google Play reviews (English, US store). Classified by `{MODEL}`.")
L.append("- Human check on 50 random reviews: 78% raw agreement on category, 90% on sentiment; "
         "most disagreements were human errors or ambiguous reviews.")
L.append("- Small weekly counts: treat changes under 5 reviews as signals, not trends.")

report = "\n".join(L)

os.makedirs(REPORT_DIR, exist_ok=True)
path = f"{REPORT_DIR}/weekly_report_{end:%Y-%m-%d}.md"
with open(path, "w", encoding="utf-8") as f:
    f.write(report)

print(report)
print("\nSaved to:", path)
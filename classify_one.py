import os
import json
from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

MODEL = "gemini-3.5-flash-lite"

# المراجعة التي نريد تصنيفها
review = "Game crashes every time after the new update, I lost my rank. Fix it!"

# التعليمات (Prompt) التي نعطيها للنموذج
prompt = f"""You classify mobile game player reviews.

Categories (choose exactly one):
- bug: crashes, errors, things not working
- feature_request: asks for new content or features
- performance: lag, FPS drops, battery, loading time
- monetization: ads, prices, in-app purchases
- praise: positive feedback only
- other: anything else

Sentiment: positive, negative, or mixed.

Return JSON with keys: category, sentiment, summary (max 15 words, English).

Review: {review}
"""

response = client.models.generate_content(
    model=MODEL,
    contents=prompt,
    config=types.GenerateContentConfig(
        response_mime_type="application/json",  # نطلب JSON فقط
        temperature=0,  # نفس الجواب تقريبًا في كل مرة
    ),
)

# الرد الخام من النموذج: نص
raw = response.text
print("Type before:", type(raw))

# نحوّل النص إلى dictionary
result = json.loads(raw)
print("Type after:", type(result))

# الآن نستطيع أخذ كل قيمة وحدها
print("Category:", result["category"])
print("Sentiment:", result["sentiment"])
print("Summary:", result["summary"])
# التصنيفات المسموحة فقط
ALLOWED_CATEGORIES = {"bug", "feature_request", "performance", "monetization", "praise", "other"}
ALLOWED_SENTIMENTS = {"positive", "negative", "mixed"}

# نفحص التصنيف
if result["category"] not in ALLOWED_CATEGORIES:
    print("⚠️ Invalid category:", result["category"])
else:
    print("✅ Category is valid")

# نفحص المشاعر
if result["sentiment"] not in ALLOWED_SENTIMENTS:
    print("⚠️ Invalid sentiment:", result["sentiment"])
else:
    print("✅ Sentiment is valid")
import os
from dotenv import load_dotenv
from google import genai

# 1) نقرأ المفتاح من ملف .env
load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

# 2) نتأكد أن المفتاح موجود قبل أن نكمل
if not api_key:
    raise SystemExit("GEMINI_API_KEY not found. Check your .env file.")

# 3) ننشئ الاتصال مع Gemini
client = genai.Client(api_key=api_key)

# 4) نرسل سؤالًا ونستقبل الرد
response = client.models.generate_content(
    model="gemini-3.5-flash-lite",
    contents="Say hello to Najwa in one short sentence.",
)

# 5) نطبع الرد
print(response.text)
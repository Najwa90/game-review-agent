import os
import json
from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

MODEL = "gemini-3.1-flash-lite"
ALLOWED_CATEGORIES = {
    "bug", "feature_request", "performance", "monetization",
    "matchmaking", "misleading_ads", "praise", "other",
}
ALLOWED_SENTIMENTS = {"positive", "negative", "mixed", "neutral"}

PROMPT_TEMPLATE = """You classify mobile game player reviews.

Categories (choose exactly one):
- bug: crashes, errors, things not working
- feature_request: asks for new content or features
- performance: lag, FPS drops, battery, loading time
- monetization: ads, prices, in-app purchases, pay-to-win, nerfs to paid items
- matchmaking: unfair matches, bad or weak teammates, too many bots, skill or level gaps between players
- misleading_ads: the game is different from what its advertisements showed
- praise: positive feedback only
- other: anything else, including unclear or off-topic text

Sentiment: positive, negative, mixed, or neutral.

If the review text is unclear, use category "other" and say "Unclear review" in the summary. Do not guess its meaning.

Return JSON with keys: category, sentiment, summary (max 15 words, English).

Review: {review}
"""


def classify_review(review):
    """Classify one review. Returns a dict with category, sentiment, summary, valid."""
    prompt = PROMPT_TEMPLATE.format(review=review)

    response = client.models.generate_content(
        model=MODEL,
        contents=prompt,
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            temperature=0,
        ),
    )

    try:
        result = json.loads(response.text)
    except json.JSONDecodeError:
        return {"category": None, "sentiment": None, "summary": None, "valid": False}

    result["valid"] = (
        result.get("category") in ALLOWED_CATEGORIES
        and result.get("sentiment") in ALLOWED_SENTIMENTS
    )
    return result


if __name__ == "__main__":
    test_reviews = [
        "Game crashes every time after the new update, I lost my rank. Fix it!",
        "always giving noobs teammates and too many bots",
        "Totally different game than shown in the advertisement.",
        "Gogo karti hui game",
        "Oyun çok güzel ama silahlar çok pahalı.",
    ]

    for i, review in enumerate(test_reviews, start=1):
        result = classify_review(review)
        print(f"\n--- Review {i} ---")
        print("Text:     ", review)
        print("Category: ", result.get("category"))
        print("Sentiment:", result.get("sentiment"))
        print("Summary:  ", result.get("summary"))
        print("Valid:    ", result.get("valid"))
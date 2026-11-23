# Game Review Agent 🎮

An LLM pipeline that turns raw Google Play reviews of a mobile shooter (**Critical Strike**) into a verified, automated **weekly report** for dev, product and marketing teams.

**Business question:** *What are players complaining about this week, what changed since last week, and what should each team do about it?*

➡️ **See an example output:** [`reports/weekly_report_2026-11-20.md`](reports/weekly_report_2026-11-20.md)

---

## How it works

```
Google Play reviews ──► Filter (4+ words) ──► LLM classification ──► Validation + retry
       (500)                (218)              (Gemini, JSON)          (allowed labels)
                                                                              │
Weekly report ◄── LLM summary (numbers only) ◄── KPIs computed in pandas ◄────┘
```

1. **Collect:** fetch the newest 500 English reviews (`fetch_reviews.py`). Usernames are not stored.
2. **Filter:** 56% of reviews have 1–3 words ("nice", "good game"). They carry no topic, so they are counted in statistics but **not sent to the LLM**, which saves 56% of API calls.
3. **Classify:** each review gets a `category`, `sentiment` and short `summary` as JSON (`classifier.py`).
4. **Validate:** every answer is checked against the allowed labels. Invalid or failed rows are retried with **exponential backoff**, and only failed rows are re-run (`retry_invalid.py`).
5. **Report:** pandas computes all numbers (this week vs. last week). The LLM only writes insights and recommendations **from those numbers** (`weekly_report.py`).

**Categories:** `bug`, `performance`, `monetization`, `matchmaking`, `misleading_ads`, `feature_request`, `praise`, `other`
**Sentiment:** `positive`, `negative`, `mixed`, `neutral`

---

## Key findings (Oct 12 – Nov 20, 2026)

| Finding | Evidence |
|---|---|
| **Monetization is the #1 complaint** | 26% of topic reviews, average **1.77★** |
| It is a **trust problem, not a price problem** | Most-liked complaint (**228 👍**): paid items get nerfed, so players must pay again |
| **Bugs are rare but painful** | Only 6% of reviews, but the lowest rating: **1.29★** |
| **Misleading ads hurt ratings** | Average **1.67★**; players compare the game to CS2 / Counter-Strike |
| Ratings are polarized | 70% five-star, 17% one-star |

Last week (Nov 13–20): monetization complaints **+5**, one-star share **14.7% → 16.8%**.

---

## Evaluation: can we trust the labels?

I labeled **50 random reviews myself, blind** (without seeing the model's labels), then compared (`evaluate.py`).

| Metric | Result |
|---|---|
| Category agreement | **78%** (39/50) |
| Sentiment agreement | **90%** (45/50) |
| Monetization (top complaint) | **7/7** |

I then reviewed all 11 category disagreements (`adjudicate.py`): **7 were my own labeling errors** (e.g. I missed sarcasm: *"awesome game!!!, if you pay"*), and **4 were genuinely ambiguous**. I found no clear model error on the remaining 46 reviews.

**Caveats (honest limits):**
- One annotator, and the disagreement review was **not blind**, so it may favor the model.
- Small sample: by the rule of three, the true category accuracy is likely **≥ ~93%**, not "100%".
- Rare categories (`performance`, `misleading_ads`) had only 1 example each in the sample.
- **Next step:** a second independent annotator.

The weekly report summary was also checked by hand: **9/9 numbers** in the LLM text match the tables.

---

## Engineering decisions

| Decision | Why |
|---|---|
| `gemini-3.1-flash-lite` for classification | On the same 10 reviews: **22s vs. 146s** and **0 vs. 6 failures** compared with `gemini-3.5-flash-lite`; same 10/10 categories. Simple, high-volume task, so speed and cost matter most. |
| JSON output + label validation | Caught the model inventing a label (`neutral`) that was not in the list. I then added it on purpose. |
| Exponential backoff (10s → 20s → 40s) | Logs showed `429 RESOURCE_EXHAUSTED` (rate limit). Final failures went from **9 to 0**, at the cost of runtime (11 → 19 min). |
| "Unclear text → `other`, do not guess" rule | The model was inventing meanings for unreadable reviews (hallucination). One prompt rule fixed it. |
| Taxonomy from the data | Reading the `other` bucket by hand revealed two hidden topics, so I added `matchmaking` and `misleading_ads`. |
| Code computes numbers, LLM writes text | Prevents invented numbers in the report. If the LLM fails, the report still ships with valid numbers (retry + fallback model). |
| `temperature=0` for labels | Labels stay stable. Free-text summaries still vary slightly, so no statistics are built on them. |

---

## Limitations

- One label per review. A review with praise **and** a
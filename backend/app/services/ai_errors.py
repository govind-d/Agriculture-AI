"""
Shared handling for Google Gemini quota errors.

The free tier allows a limited number of requests per day *per model*, so an
exhausted quota is a normal operating condition rather than a bug — it deserves
a message that says what happened and what to do about it.
"""

QUOTA_MESSAGE = (
    "The daily free AI limit for this Gemini model has been used up. "
    "It resets every day, or you can set a different GEMINI_MODEL in "
    "backend/.env (each model has its own limit)."
)


def is_quota_error(error: Exception) -> bool:
    """True when Gemini refused the request because a quota/rate limit was hit."""
    text = str(error).lower()
    return "429" in text or "quota" in text or "rate limit" in text

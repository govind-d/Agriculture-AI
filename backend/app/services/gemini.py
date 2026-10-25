"""
Gemini model access with automatic fallback.

The free tier allows a small number of requests per day *per model*, so one
model running out is routine. `gemini_model()` returns a stand-in for
`genai.GenerativeModel` that transparently moves to the next configured model
when the current one reports an exhausted quota, and remembers which models are
spent so later requests don't waste a round trip on them.
"""

import google.generativeai as genai

from app.core.config import settings
from app.services.ai_errors import is_quota_error

# Models known to have hit their quota in this process, skipped until restart
_exhausted: set[str] = set()


def _candidates() -> list[str]:
    """Configured models, preferred first, without duplicates."""
    names = [settings.GEMINI_MODEL] + [
        name.strip() for name in settings.GEMINI_FALLBACK_MODELS.split(",")
    ]
    ordered = list(dict.fromkeys(name for name in names if name))

    fresh = [name for name in ordered if name not in _exhausted]
    # All spent? Quotas reset daily, so try again rather than fail outright.
    if not fresh:
        _exhausted.clear()
        return ordered
    return fresh


class _FallbackModel:
    """Mimics the bit of genai.GenerativeModel the routers use."""

    async def generate_content_async(self, contents, **kwargs):
        return await self._run(contents, kwargs, is_async=True)

    def generate_content(self, contents, **kwargs):
        return self._run(contents, kwargs, is_async=False)

    def _run(self, contents, kwargs, is_async: bool):
        genai.configure(api_key=settings.GEMINI_API_KEY)
        names = _candidates()

        async def _async_attempt():
            last_error = None
            for name in names:
                model = genai.GenerativeModel(name)
                try:
                    return await model.generate_content_async(contents, **kwargs)
                except Exception as error:
                    if not is_quota_error(error):
                        raise
                    print(f"Gemini quota exhausted for {name}; trying the next model")
                    _exhausted.add(name)
                    last_error = error
            raise last_error

        if is_async:
            return _async_attempt()

        last_error = None
        for name in names:
            model = genai.GenerativeModel(name)
            try:
                return model.generate_content(contents, **kwargs)
            except Exception as error:
                if not is_quota_error(error):
                    raise
                print(f"Gemini quota exhausted for {name}; trying the next model")
                _exhausted.add(name)
                last_error = error
        raise last_error


def gemini_model() -> _FallbackModel:
    """Drop-in replacement for genai.GenerativeModel(...) with model fallback."""
    return _FallbackModel()

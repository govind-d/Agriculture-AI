"""
Crop prices routes — data.gov.in API integration with caching.
"""

from fastapi import APIRouter, HTTPException, Depends
from datetime import datetime, timedelta, timezone
import json
import google.generativeai as genai

from app.core.database import get_db
from app.core.config import settings
from app.core.security import get_current_user

router = APIRouter()

# Common crops and markets for Indian agriculture
COMMON_CROPS = [
    "Rice", "Wheat", "Maize", "Cotton", "Sugarcane",
    "Potato", "Tomato", "Onion", "Soybean", "Groundnut",
    "Mustard", "Jowar", "Bajra", "Ragi", "Barley",
]

COMMON_MARKETS = [
    "Delhi", "Mumbai", "Chennai", "Kolkata", "Bengaluru",
    "Hyderabad", "Pune", "Ahmedabad", "Jaipur", "Lucknow",
]


@router.get("/")
async def get_crop_prices(
    crop: str = "Rice",
    market: str = "Delhi",
    user: dict = Depends(get_current_user),
):
    """Get current crop prices for a specific crop and market."""
    db = get_db()
    cache_key_crop = crop.lower().strip()
    cache_key_market = market.lower().strip()

    # Check cache first
    cached = await db.crop_price_cache.find_one({
        "cropType": cache_key_crop,
        "market": cache_key_market,
    })

    if cached:
        return {
            "cropType": crop,
            "market": market,
            "price": cached["price"],
            "unit": cached["unit"],
            "priceDate": cached["priceDate"],
            "source": "cached",
        }

    # Try fetching estimated price from Gemini API
    if settings.GEMINI_API_KEY:
        try:
            price_data = await _fetch_price_from_gemini(crop, market)
            if price_data:
                # Cache the result
                await db.crop_price_cache.update_one(
                    {"cropType": cache_key_crop, "market": cache_key_market},
                    {
                        "$set": {
                            "price": price_data["price"],
                            "unit": price_data["unit"],
                            "priceDate": price_data["priceDate"],
                            "fetchedAt": datetime.now(timezone.utc),
                            "expiresAt": datetime.now(timezone.utc) + timedelta(hours=24),
                        }
                    },
                    upsert=True,
                )
                return {**price_data, "source": "gemini"}
        except Exception:
            pass

    # Fallback to mock data for demo
    mock_price = _get_mock_price(crop, market)
    return {**mock_price, "source": "demo"}


@router.get("/trends")
async def get_price_trends(
    crop: str = "Rice",
    days: int = 30,
    user: dict = Depends(get_current_user),
):
    """Get price trends for a crop over time."""
    # For MVP, return simulated trend data
    import random

    trends = []
    today = datetime.now(timezone.utc).date()
    base_prices = {
        "Rice": 2200, "Wheat": 2400, "Maize": 1800,
        "Cotton": 6500, "Sugarcane": 350, "Potato": 1500,
        "Tomato": 2500, "Onion": 2000, "Soybean": 4500,
    }
    base = base_prices.get(crop, 2000)

    for i in range(days):
        d = today - timedelta(days=days - i - 1)
        variance = random.uniform(-0.08, 0.08)
        price = round(base * (1 + variance))
        trends.append({
            "date": d.strftime("%Y-%m-%d"),
            "price": price,
            "unit": "₹/quintal",
        })

    return {
        "crop": crop,
        "trends": trends,
    }


@router.get("/market-trends")
async def get_market_trends(
    crop_name: str = "Rice",
    market: str = "Delhi",
    user: dict = Depends(get_current_user),
):
    """
    Combined market overview for a crop: current price, trend direction and an
    AI-written forecast narrative. This is the shape the MarketPrices UI renders.
    """
    db = get_db()
    cache_key_crop = crop_name.lower().strip()
    cache_key_market = market.lower().strip()

    cached = await db.market_trends_cache.find_one({
        "cropType": cache_key_crop,
        "market": cache_key_market,
    })
    if cached:
        return {
            "crop": crop_name,
            "market": market,
            "currentPrice": cached["currentPrice"],
            "trend": cached["trend"],
            "forecast": cached["forecast"],
            "source": "cached",
        }

    overview = None
    if settings.GEMINI_API_KEY:
        overview = await _fetch_market_trends_from_gemini(crop_name, market)

    if overview is None:
        overview = _get_mock_market_trends(crop_name, market)
        source = "demo"
    else:
        source = "gemini"
        await db.market_trends_cache.update_one(
            {"cropType": cache_key_crop, "market": cache_key_market},
            {
                "$set": {
                    "currentPrice": overview["currentPrice"],
                    "trend": overview["trend"],
                    "forecast": overview["forecast"],
                    "fetchedAt": datetime.now(timezone.utc),
                    "expiresAt": datetime.now(timezone.utc) + timedelta(hours=12),
                }
            },
            upsert=True,
        )

    return {"crop": crop_name, "market": market, **overview, "source": source}


@router.get("/crops")
async def list_available_crops():
    """List available crops for price queries."""
    return {"crops": COMMON_CROPS}


@router.get("/markets")
async def list_available_markets():
    """List available markets."""
    return {"markets": COMMON_MARKETS}


async def _fetch_price_from_gemini(crop: str, market: str) -> dict | None:
    """Fetch estimated crop prices using Gemini API."""
    genai.configure(api_key=settings.GEMINI_API_KEY)
    model = genai.GenerativeModel("gemini-3.6-flash")
    
    prompt = f"""
    You are an agricultural data assistant. Provide a realistic current market price for {crop} in the {market} market in India.
    Respond ONLY with a valid JSON object in the following format, with no markdown formatting or other text:
    {{
        "cropType": "{crop}",
        "market": "{market}",
        "price": <estimated_price_in_INR_as_number>,
        "unit": "₹/quintal",
        "priceDate": "{datetime.now(timezone.utc).strftime('%Y-%m-%d')}"
    }}
    """
    
    try:
        response = await model.generate_content_async(prompt)
        text = response.text.strip()
        if text.startswith('```json'):
            text = text[7:-3].strip()
        elif text.startswith('```'):
            text = text[3:-3].strip()
            
        data = json.loads(text)
        return {
            "cropType": crop,
            "market": market,
            "price": float(data.get("price", 0)),
            "unit": "₹/quintal",
            "priceDate": data.get("priceDate", datetime.now(timezone.utc).strftime("%Y-%m-%d")),
        }
    except Exception:
        return None


def _get_mock_price(crop: str, market: str) -> dict:
    """Return mock price data for demo."""
    mock_prices = {
        "Rice": 2200, "Wheat": 2400, "Maize": 1800,
        "Cotton": 6500, "Sugarcane": 350, "Potato": 1500,
        "Tomato": 2500, "Onion": 2000, "Soybean": 4500,
        "Groundnut": 5500, "Mustard": 5000, "Jowar": 3000,
        "Bajra": 2350, "Ragi": 3578, "Barley": 1735,
    }
    return {
        "cropType": crop,
        "market": market,
        "price": mock_prices.get(crop, 2000),
        "unit": "₹/quintal",
        "priceDate": datetime.now(timezone.utc).strftime("%Y-%m-%d"),
    }


VALID_TRENDS = {"Rising", "Falling", "Stable"}


async def _fetch_market_trends_from_gemini(crop: str, market: str) -> dict | None:
    """Ask Gemini for current price, trend direction and a short forecast narrative."""
    genai.configure(api_key=settings.GEMINI_API_KEY)
    model = genai.GenerativeModel("gemini-3.6-flash")

    prompt = f"""
    You are an agricultural market analyst. Give a realistic current market assessment
    for {crop} in the {market} market in India.
    Respond ONLY with a valid JSON object, no markdown fences and no other text:
    {{
        "price": <current_price_in_INR_per_quintal_as_number>,
        "trend": "Rising" | "Falling" | "Stable",
        "forecast": "<2-4 sentences on the near-term price outlook and the main factors driving it>"
    }}
    """

    try:
        response = await model.generate_content_async(prompt)
        text = response.text.strip()
        if text.startswith("```json"):
            text = text[7:-3].strip()
        elif text.startswith("```"):
            text = text[3:-3].strip()

        data = json.loads(text)
        trend = str(data.get("trend", "Stable")).strip().capitalize()
        if trend not in VALID_TRENDS:
            trend = "Stable"

        forecast = str(data.get("forecast", "")).strip()
        if not forecast:
            return None

        return {
            "currentPrice": {
                "price": round(float(data["price"]), 2),
                "unit": "quintal",
            },
            "trend": trend,
            "forecast": forecast,
        }
    except Exception:
        return None


def _get_mock_market_trends(crop: str, market: str) -> dict:
    """Deterministic fallback overview when Gemini is unavailable."""
    base = _get_mock_price(crop, market)
    return {
        "currentPrice": {"price": base["price"], "unit": "quintal"},
        "trend": "Stable",
        "forecast": (
            f"Demo data - no live market feed is configured, so this is an indicative "
            f"price for {crop} in {market}. Set GEMINI_API_KEY in backend/.env to get a "
            f"real AI-generated price outlook."
        ),
    }

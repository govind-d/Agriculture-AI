"""
Weather service — OpenWeatherMap integration with MongoDB TTL caching.
Adapted from smart-agriculture-ai/services/weather_service.py
"""

import httpx
from datetime import datetime, timedelta, timezone

from app.core.config import settings
from app.core.database import get_db


async def get_current_weather(city: str) -> dict:
    """
    Get current weather for a city.
    Checks MongoDB cache first, falls back to OpenWeatherMap API.
    """
    db = get_db()
    cache_key = f"current_{city.lower().strip()}"

    # Check cache
    cached = await db.weather_cache.find_one({"locationKey": cache_key})
    if cached:
        return cached["forecastJson"]

    # Fetch from API
    if not settings.OPENWEATHER_API_KEY:
        return _mock_weather(city)

    url = (
        f"http://api.openweathermap.org/data/2.5/weather"
        f"?q={city}&appid={settings.OPENWEATHER_API_KEY}&units=metric"
    )

    async with httpx.AsyncClient(timeout=10) as client:
        response = await client.get(url)

    if response.status_code != 200:
        data = response.json()
        raise ValueError(data.get("message", "Weather API error"))

    data = response.json()
    weather_data = {
        "city": city,
        "temperature": data["main"]["temp"],
        "feelsLike": data["main"]["feels_like"],
        "humidity": data["main"]["humidity"],
        "pressure": data["main"]["pressure"],
        "description": data["weather"][0]["description"].title(),
        "icon": data["weather"][0]["icon"],
        "windSpeed": data["wind"]["speed"],
        "visibility": data.get("visibility", 0),
        "advice": _generate_weather_advice(data),
    }

    # Cache for 30 minutes
    await db.weather_cache.update_one(
        {"locationKey": cache_key},
        {
            "$set": {
                "forecastJson": weather_data,
                "fetchedAt": datetime.now(timezone.utc),
                "expiresAt": datetime.now(timezone.utc) + timedelta(minutes=30),
            }
        },
        upsert=True,
    )

    return weather_data


async def get_weather_forecast(city: str, days: int = 5) -> list:
    """
    Get weather forecast. Uses 5-day/3-hour endpoint from OpenWeatherMap (free tier).
    """
    db = get_db()
    cache_key = f"forecast_{city.lower().strip()}_{days}"

    # Check cache
    cached = await db.weather_cache.find_one({"locationKey": cache_key})
    if cached:
        return cached["forecastJson"]

    if not settings.OPENWEATHER_API_KEY:
        return _mock_forecast(city, days)

    url = (
        f"http://api.openweathermap.org/data/2.5/forecast"
        f"?q={city}&appid={settings.OPENWEATHER_API_KEY}&units=metric&cnt={days * 8}"
    )

    async with httpx.AsyncClient(timeout=10) as client:
        response = await client.get(url)

    if response.status_code != 200:
        data = response.json()
        raise ValueError(data.get("message", "Forecast API error"))

    data = response.json()

    # Group by day and average
    daily = {}
    for item in data.get("list", []):
        date_str = item["dt_txt"][:10]
        if date_str not in daily:
            daily[date_str] = {
                "temps": [],
                "humidity": [],
                "descriptions": [],
                "wind": [],
            }
        daily[date_str]["temps"].append(item["main"]["temp"])
        daily[date_str]["humidity"].append(item["main"]["humidity"])
        daily[date_str]["descriptions"].append(
            item["weather"][0]["description"]
        )
        daily[date_str]["wind"].append(item["wind"]["speed"])

    forecast = []
    for date_str, vals in daily.items():
        import statistics

        forecast.append({
            "date": date_str,
            "temperature": round(statistics.mean(vals["temps"]), 1),
            "humidity": round(statistics.mean(vals["humidity"]), 1),
            "windSpeed": round(statistics.mean(vals["wind"]), 1),
            "description": max(
                set(vals["descriptions"]),
                key=vals["descriptions"].count,
            ).title(),
        })

    # Cache for 1 hour
    await db.weather_cache.update_one(
        {"locationKey": cache_key},
        {
            "$set": {
                "forecastJson": forecast,
                "fetchedAt": datetime.now(timezone.utc),
                "expiresAt": datetime.now(timezone.utc) + timedelta(hours=1),
            }
        },
        upsert=True,
    )

    return forecast


def _generate_weather_advice(data: dict) -> list:
    """Generate farming advice based on current weather conditions."""
    advice = []
    temp = data["main"]["temp"]
    humidity = data["main"]["humidity"]
    wind = data["wind"]["speed"]
    description = data["weather"][0]["main"].lower()

    if temp > 38:
        advice.append("🌡️ Extreme heat — increase irrigation frequency and provide shade for sensitive crops.")
    elif temp > 35:
        advice.append("🌡️ High temperature — ensure adequate watering, especially for young plants.")
    elif temp < 5:
        advice.append("❄️ Frost risk — protect crops with mulch or row covers.")
    elif temp < 10:
        advice.append("🥶 Cold conditions — delay planting of warm-season crops.")

    if humidity > 85:
        advice.append("💧 Very high humidity — increased risk of fungal diseases. Monitor plants closely.")
    elif humidity > 75:
        advice.append("💧 High humidity — good for most crops but watch for leaf diseases.")
    elif humidity < 30:
        advice.append("🏜️ Low humidity — increase irrigation and consider mulching.")

    if wind > 15:
        advice.append("💨 Strong winds — postpone pesticide spraying. Provide windbreaks for young plants.")

    if "rain" in description:
        advice.append("🌧️ Rain expected — delay fertilizer application to prevent runoff.")
    elif "thunder" in description or "storm" in description:
        advice.append("⛈️ Storm warning — secure greenhouse covers and protect delicate crops.")

    if not advice:
        advice.append("✅ Weather conditions are favorable for farming activities.")

    return advice


def _mock_weather(city: str) -> dict:
    """Return mock weather when no API key is configured."""
    return {
        "city": city,
        "temperature": 28.5,
        "feelsLike": 30.2,
        "humidity": 65,
        "pressure": 1013,
        "description": "Partly Cloudy",
        "icon": "02d",
        "windSpeed": 3.5,
        "visibility": 10000,
        "advice": ["ℹ️ Using demo data. Set OPENWEATHER_API_KEY for live weather."],
    }


def _mock_forecast(city: str, days: int) -> list:
    """Return mock forecast when no API key is configured."""
    from datetime import date

    forecast = []
    today = date.today()
    for i in range(days):
        d = today + timedelta(days=i)
        forecast.append({
            "date": d.strftime("%Y-%m-%d"),
            "temperature": round(25 + (i * 0.5), 1),
            "humidity": 60 + i,
            "windSpeed": 3.0,
            "description": "Partly Cloudy",
        })
    return forecast

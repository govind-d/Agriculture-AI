"""
Weather routes — current weather and forecast.
"""

from fastapi import APIRouter, HTTPException, Depends
from app.core.security import get_current_user
from app.services.weather_service import get_current_weather, get_weather_forecast

router = APIRouter()


@router.get("/current")
async def current_weather(
    city: str = "New Delhi",
    user: dict = Depends(get_current_user),
):
    """Get current weather for a city."""
    try:
        data = await get_current_weather(city)
        return data
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/forecast")
async def weather_forecast(
    city: str = "New Delhi",
    days: int = 5,
    user: dict = Depends(get_current_user),
):
    """Get weather forecast for a city (up to 5 days on free tier)."""
    if days < 1 or days > 16:
        raise HTTPException(status_code=400, detail="Days must be between 1 and 16.")

    try:
        data = await get_weather_forecast(city, days)
        return {"city": city, "forecast": data}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

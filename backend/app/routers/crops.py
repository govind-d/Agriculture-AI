"""
Crop recommendation routes.
"""

from fastapi import APIRouter, Depends

from app.core.security import get_current_user
from app.models.schemas import CropRecommendationRequest
from app.services.validation import validate_and_clip_crop_inputs
from app.core.config import settings
import google.generativeai as genai
import json

router = APIRouter()


@router.post("/recommend")
async def recommend_crop(
    req: CropRecommendationRequest,
    user: dict = Depends(get_current_user),
):
    """
    Get crop recommendations based on soil and weather parameters.
    Returns top 3 crops with probabilities and feature importance.
    """
    from fastapi import HTTPException

    # Validate and clip inputs
    temperature, humidity, rainfall, ph, n, p, k, warnings = (
        validate_and_clip_crop_inputs(
            req.nitrogen, req.phosphorus, req.potassium,
            req.ph, req.temperature, req.humidity, req.rainfall,
        )
    )
    
    if not settings.GEMINI_API_KEY:
        raise HTTPException(status_code=503, detail="Gemini API key not configured.")
        
    genai.configure(api_key=settings.GEMINI_API_KEY)
    model = genai.GenerativeModel("gemini-3.6-flash")
    
    prompt = f"""
    You are an expert agronomist. Based on the following soil and weather conditions in India, recommend the best crop to grow.
    Nitrogen (N): {n}
    Phosphorus (P): {p}
    Potassium (K): {k}
    Temperature: {temperature}°C
    Humidity: {humidity}%
    pH Level: {ph}
    Rainfall: {rainfall}mm
    
    Respond ONLY with a valid JSON object in this format:
    {{
        "recommendedCrop": "Crop Name",
        "confidence": 0.95,
        "alternatives": ["Alt Crop 1", "Alt Crop 2"],
        "reasoning": "A short explanation of why this crop is suitable."
    }}
    """
    
    try:
        response = await model.generate_content_async(prompt)
        text = response.text.strip()
        if text.startswith('```json'):
            text = text[7:-3].strip()
        elif text.startswith('```'):
            text = text[3:-3].strip()
            
        result = json.loads(text)
    except Exception as e:
        print(f"Gemini error: {e}")
        raise HTTPException(
            status_code=500,
            detail="Error getting crop recommendation from AI. Please try again."
        )

    return {
        **result,
        "warnings": warnings,
    }

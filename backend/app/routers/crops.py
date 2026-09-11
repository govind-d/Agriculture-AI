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
        "topCrops": [
            {{"crop": "Crop Name", "confidence": 0.95}},
            {{"crop": "Alternative Crop 1", "confidence": 0.80}},
            {{"crop": "Alternative Crop 2", "confidence": 0.65}}
        ],
        "insight": "A short explanation of why these crops are suitable."
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
        
        # Ensure frontend compatibility (topCrops and insight must be present)
        if "topCrops" not in result:
            recommended_crop = result.get("recommendedCrop", "Unknown Crop")
            confidence = result.get("confidence", 1.0)
            alternatives = result.get("alternatives", [])
            
            top_crops = [{"crop": recommended_crop, "confidence": confidence}]
            alt_confidence = confidence
            for alt in alternatives:
                alt_confidence = max(0.1, alt_confidence - 0.15)
                top_crops.append({"crop": alt, "confidence": alt_confidence})
            result["topCrops"] = top_crops
            
        if "insight" not in result:
            result["insight"] = result.get("reasoning", "Suitable conditions for crop cultivation.")
            
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


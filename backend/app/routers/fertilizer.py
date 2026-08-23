"""
Fertilizer recommendation routes.
"""

from fastapi import APIRouter, HTTPException, Depends

from app.core.security import get_current_user
from app.models.schemas import FertilizerRecommendationRequest
from app.services.validation import validate_and_clip_fertilizer_inputs
from app.core.config import settings
import google.generativeai as genai
import json

router = APIRouter()

SOIL_TYPES = ["Sandy", "Loamy", "Black", "Red", "Clayey"]
CROP_TYPES = ["Wheat", "Rice", "Maize", "Sugarcane", "Cotton"]


@router.post("/recommend")
async def recommend_fertilizer(
    req: FertilizerRecommendationRequest,
    user: dict = Depends(get_current_user),
):
    """
    Get fertilizer recommendation based on soil and crop parameters.
    Returns fertilizer type, quantity per acre, and explanation.
    """
    # Validate and clip inputs
    temperature, humidity, moisture, n, p, k, land_area, warnings = (
        validate_and_clip_fertilizer_inputs(
            req.nitrogen, req.phosphorus, req.potassium,
            req.temperature, req.humidity, req.moisture, req.landArea,
        )
    )

    if not settings.GEMINI_API_KEY:
        raise HTTPException(status_code=503, detail="Gemini API key not configured.")
        
    genai.configure(api_key=settings.GEMINI_API_KEY)
    model = genai.GenerativeModel("gemini-3.6-flash")
    
    prompt = f"""
    You are an expert agronomist. Recommend the best fertilizer based on the following field conditions:
    Soil Type: {req.soilType}
    Crop Type: {req.cropType}
    Nitrogen (N): {n}
    Phosphorus (P): {p}
    Potassium (K): {k}
    Temperature: {temperature}°C
    Humidity: {humidity}%
    Moisture: {moisture}
    Land Area: {land_area} acres
    
    Respond ONLY with a valid JSON object in this format:
    {{
        "fertilizer": "Name of the Fertilizer (e.g., Urea, DAP, NPK 14-35-14)",
        "qtyPerAcre": 50.0,
        "explanation": "A short explanation of why this fertilizer is recommended based on the NPK values."
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
        
        # Calculate total quantity based on acreage
        qty_per_acre = float(result.get("qtyPerAcre", 50))
        total_qty = qty_per_acre * land_area
        
        result["qtyPerAcre"] = qty_per_acre
        result["totalQty"] = total_qty
        
    except Exception as e:
        print(f"Gemini error: {e}")
        raise HTTPException(
            status_code=500,
            detail="Error getting fertilizer recommendation from AI. Please try again."
        )

    return {
        **result,
        "warnings": warnings,
    }


@router.get("/soil-types")
async def list_soil_types():
    """Get available soil types for the fertilizer model."""
    return {"soilTypes": SOIL_TYPES}


@router.get("/crop-types")
async def list_crop_types():
    """Get available crop types for the fertilizer model."""
    return {"cropTypes": CROP_TYPES}

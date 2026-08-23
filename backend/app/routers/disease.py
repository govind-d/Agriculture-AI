"""
Disease detection routes — image upload → ML inference → result.
"""

from fastapi import APIRouter, HTTPException, Depends, UploadFile, File, Form
from datetime import datetime, timezone
from bson import ObjectId
from typing import Optional

from app.core.database import get_db
from app.core.security import get_current_user
from app.core.config import settings
from app.services.cloudinary_service import upload_image
import google.generativeai as genai
import json

router = APIRouter()


@router.post("/analyze")
async def analyze_disease(
    image: UploadFile = File(...),
    farmId: Optional[str] = Form(None),
    cropId: Optional[str] = Form(None),
    user: dict = Depends(get_current_user),
):
    """
    Upload a plant leaf image for disease detection.
    Returns disease name, confidence score, and treatment recommendations.
    """
    # Read image bytes
    image_bytes = await image.read()

    if len(image_bytes) == 0:
        raise HTTPException(status_code=400, detail="Empty image file.")

    if len(image_bytes) > 10 * 1024 * 1024:  # 10MB limit
        raise HTTPException(status_code=400, detail="Image too large. Maximum 10MB.")

    # Upload to Cloudinary first so we have the URL
    image_url = await upload_image(image_bytes)

    # Analyze with Gemini
    if not settings.GEMINI_API_KEY:
        raise HTTPException(status_code=503, detail="Gemini API key not configured.")
        
    genai.configure(api_key=settings.GEMINI_API_KEY)
    model = genai.GenerativeModel("gemini-3.6-flash")
    
    prompt = """
    You are an expert plant pathologist. Analyze this image of a plant leaf.
    Determine if it is healthy or if it has a disease. If the image is clearly not a plant leaf, set detectedDisease to "Not a leaf".
    Respond ONLY with a valid JSON object in the following format:
    {
        "detectedDisease": "<Disease Name or 'Healthy' or 'Not a leaf'>",
        "confidenceScore": <number between 0.0 and 1.0>,
        "lowConfidence": <boolean true if confidence < 0.6>,
        "recommendedAction": "<A short paragraph with treatment recommendations>"
    }
    """
    
    try:
        response = await model.generate_content_async(
            contents=[prompt, {"mime_type": "image/jpeg", "data": image_bytes}]
        )
        text = response.text.strip()
        if text.startswith('```json'):
            text = text[7:-3].strip()
        elif text.startswith('```'):
            text = text[3:-3].strip()
            
        result = json.loads(text)
        
        if result.get("detectedDisease") == "Not a leaf":
            raise HTTPException(
                status_code=400,
                detail="The uploaded image does not appear to be a plant leaf. Please upload a clear leaf image.",
            )
            
    except HTTPException:
        raise
    except Exception as e:
        print(f"Gemini error: {e}")
        raise HTTPException(
            status_code=500,
            detail="Error analyzing image with AI. Please try again."
        )

    # Save detection record
    db = get_db()
    detection_doc = {
        "farmerId": ObjectId(user["_id"]) if isinstance(user["_id"], str) else user["_id"],
        "farmId": ObjectId(farmId) if farmId else None,
        "cropId": ObjectId(cropId) if cropId else None,
        "imageUrl": image_url,
        "detectedDisease": result["detectedDisease"],
        "confidenceScore": result["confidenceScore"],
        "lowConfidence": result["lowConfidence"],
        "recommendedAction": result["recommendedAction"],
        "detectedAt": datetime.now(timezone.utc),
    }

    insert_result = await db.disease_detections.insert_one(detection_doc)

    return {
        "id": str(insert_result.inserted_id),
        "imageUrl": image_url,
        **result,
        "detectedAt": detection_doc["detectedAt"].isoformat(),
    }


@router.get("/history/{crop_id}")
async def get_detection_history(
    crop_id: str,
    limit: int = 20,
    user: dict = Depends(get_current_user),
):
    """Get disease detection history for a specific crop."""
    db = get_db()

    cursor = (
        db.disease_detections.find({"cropId": ObjectId(crop_id)})
        .sort("detectedAt", -1)
        .limit(limit)
    )

    detections = []
    async for doc in cursor:
        detections.append({
            "id": str(doc["_id"]),
            "imageUrl": doc["imageUrl"],
            "detectedDisease": doc["detectedDisease"],
            "confidenceScore": doc["confidenceScore"],
            "lowConfidence": doc.get("lowConfidence", False),
            "recommendedAction": doc["recommendedAction"],
            "detectedAt": doc["detectedAt"].isoformat(),
        })

    return {"detections": detections}


@router.get("/recent")
async def get_recent_detections(
    limit: int = 10,
    user: dict = Depends(get_current_user),
):
    """Get recent detections for the current user."""
    db = get_db()
    user_id = ObjectId(user["_id"]) if isinstance(user["_id"], str) else user["_id"]

    cursor = (
        db.disease_detections.find({"farmerId": user_id})
        .sort("detectedAt", -1)
        .limit(limit)
    )

    detections = []
    async for doc in cursor:
        detections.append({
            "id": str(doc["_id"]),
            "imageUrl": doc["imageUrl"],
            "detectedDisease": doc["detectedDisease"],
            "confidenceScore": doc["confidenceScore"],
            "lowConfidence": doc.get("lowConfidence", False),
            "recommendedAction": doc["recommendedAction"],
            "detectedAt": doc["detectedAt"].isoformat(),
        })

    return {"detections": detections}

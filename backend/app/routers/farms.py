"""
Farm management routes — CRUD for farms and crops.
"""

from fastapi import APIRouter, HTTPException, Depends, status
from datetime import datetime, timezone
from bson import ObjectId
from typing import Optional

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.schemas import FarmCreate, FarmUpdate, CropCreate

router = APIRouter()


def _serialize_farm(farm: dict) -> dict:
    """Convert MongoDB farm document to JSON-serializable dict."""
    farm["id"] = str(farm.pop("_id"))
    farm["farmerId"] = str(farm.get("farmerId", ""))
    if "crops" in farm:
        for crop in farm["crops"]:
            crop["cropId"] = str(crop.get("cropId", ""))
    return farm


@router.get("/{farmer_id}")
async def get_farmer_profile(farmer_id: str, user: dict = Depends(get_current_user)):
    """Get farmer profile with all farms."""
    db = get_db()

    farmer = await db.users.find_one({"_id": ObjectId(farmer_id)})
    if not farmer:
        raise HTTPException(status_code=404, detail="Farmer not found")

    farms_cursor = db.farms.find({"farmerId": ObjectId(farmer_id)})
    farms = []
    async for farm in farms_cursor:
        farms.append(_serialize_farm(farm))

    return {
        "farmer": {
            "id": str(farmer["_id"]),
            "name": farmer["name"],
            "phone": farmer["phone"],
            "email": farmer.get("email"),
            "role": farmer["role"],
            "preferredLanguage": farmer.get("preferredLanguage", "en"),
        },
        "farms": farms,
    }


@router.post("/{farmer_id}/farms", status_code=status.HTTP_201_CREATED)
async def create_farm(
    farmer_id: str,
    req: FarmCreate,
    user: dict = Depends(get_current_user),
):
    """Create a new farm for a farmer."""
    db = get_db()

    # Verify farmer exists
    farmer = await db.users.find_one({"_id": ObjectId(farmer_id)})
    if not farmer:
        raise HTTPException(status_code=404, detail="Farmer not found")

    # Build crops with generated cropIds
    crops_docs = []
    for crop in req.crops:
        crops_docs.append({
            "cropId": ObjectId(),
            "cropType": crop.cropType,
            "plantingDate": crop.plantingDate,
            "expectedHarvestDate": crop.expectedHarvestDate,
            "status": crop.status,
            "irrigationSchedule": crop.irrigationSchedule.model_dump() if crop.irrigationSchedule else None,
        })

    farm_doc = {
        "farmerId": ObjectId(farmer_id),
        "name": req.name,
        "location": req.location.model_dump(),
        "areaSize": req.areaSize,
        "soilType": req.soilType,
        "crops": crops_docs,
        "createdAt": datetime.now(timezone.utc),
    }

    result = await db.farms.insert_one(farm_doc)
    farm_doc["_id"] = result.inserted_id

    return _serialize_farm(farm_doc)


@router.put("/{farm_id}")
async def update_farm(
    farm_id: str,
    req: FarmUpdate,
    user: dict = Depends(get_current_user),
):
    """Update farm details."""
    db = get_db()

    update_data = {k: v for k, v in req.model_dump().items() if v is not None}
    if "location" in update_data:
        update_data["location"] = update_data["location"]

    if not update_data:
        raise HTTPException(status_code=400, detail="No fields to update")

    result = await db.farms.update_one(
        {"_id": ObjectId(farm_id)},
        {"$set": update_data},
    )

    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Farm not found")

    farm = await db.farms.find_one({"_id": ObjectId(farm_id)})
    return _serialize_farm(farm)


@router.post("/{farm_id}/crops", status_code=status.HTTP_201_CREATED)
async def add_crop(
    farm_id: str,
    req: CropCreate,
    user: dict = Depends(get_current_user),
):
    """Add a crop to an existing farm."""
    db = get_db()

    crop_doc = {
        "cropId": ObjectId(),
        "cropType": req.cropType,
        "plantingDate": req.plantingDate,
        "expectedHarvestDate": req.expectedHarvestDate,
        "status": req.status,
        "irrigationSchedule": req.irrigationSchedule.model_dump() if req.irrigationSchedule else None,
    }

    result = await db.farms.update_one(
        {"_id": ObjectId(farm_id)},
        {"$push": {"crops": crop_doc}},
    )

    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Farm not found")

    crop_doc["cropId"] = str(crop_doc["cropId"])
    return crop_doc


@router.delete("/{farm_id}")
async def delete_farm(farm_id: str, user: dict = Depends(get_current_user)):
    """Delete a farm."""
    db = get_db()
    result = await db.farms.delete_one({"_id": ObjectId(farm_id)})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Farm not found")
    return {"message": "Farm deleted successfully"}

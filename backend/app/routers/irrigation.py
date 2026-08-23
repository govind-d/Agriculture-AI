"""
Irrigation schedule routes.
"""

from fastapi import APIRouter, HTTPException, Depends
from datetime import datetime, timezone
from bson import ObjectId

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.schemas import IrrigationSchedule

router = APIRouter()


@router.get("/schedule/{farm_id}")
async def get_irrigation_schedule(
    farm_id: str,
    user: dict = Depends(get_current_user),
):
    """Get irrigation schedules for all crops in a farm."""
    db = get_db()

    farm = await db.farms.find_one({"_id": ObjectId(farm_id)})
    if not farm:
        raise HTTPException(status_code=404, detail="Farm not found")

    schedules = []
    for crop in farm.get("crops", []):
        schedule = crop.get("irrigationSchedule")
        if schedule:
            schedules.append({
                "cropId": str(crop["cropId"]),
                "cropType": crop["cropType"],
                "frequency": schedule.get("frequency", "daily"),
                "scheduledTime": schedule.get("scheduledTime", "06:00"),
                "lastNotifiedAt": schedule.get("lastNotifiedAt"),
                "status": crop.get("status", "active"),
            })

    return {"farmId": farm_id, "schedules": schedules}


@router.post("/schedule")
async def set_irrigation_schedule(
    farmId: str,
    cropId: str,
    schedule: IrrigationSchedule,
    user: dict = Depends(get_current_user),
):
    """Set or update irrigation schedule for a crop."""
    db = get_db()

    result = await db.farms.update_one(
        {"_id": ObjectId(farmId), "crops.cropId": ObjectId(cropId)},
        {
            "$set": {
                "crops.$.irrigationSchedule": schedule.model_dump(),
            }
        },
    )

    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Farm or crop not found")

    return {"message": "Irrigation schedule updated", "schedule": schedule.model_dump()}

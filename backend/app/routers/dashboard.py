"""
Dashboard routes — aggregated data across all services.
"""

from fastapi import APIRouter, HTTPException, Depends
from bson import ObjectId

from app.core.database import get_db
from app.core.security import get_current_user
from app.services.weather_service import get_current_weather

router = APIRouter()


@router.get("/{farmer_id}")
async def get_dashboard(
    farmer_id: str,
    user: dict = Depends(get_current_user),
):
    """
    Aggregated dashboard — combines data from all services into one response.
    """
    db = get_db()

    # 1. User profile
    farmer = await db.users.find_one({"_id": ObjectId(farmer_id)})
    if not farmer:
        raise HTTPException(status_code=404, detail="Farmer not found")

    user_data = {
        "id": str(farmer["_id"]),
        "name": farmer["name"],
        "phone": farmer["phone"],
        "email": farmer.get("email"),
        "role": farmer["role"],
    }

    # 2. Farms
    farms_cursor = db.farms.find({"farmerId": ObjectId(farmer_id)})
    farms = []
    async for farm in farms_cursor:
        farm["id"] = str(farm.pop("_id"))
        farm["farmerId"] = str(farm.get("farmerId", ""))
        if "crops" in farm:
            for crop in farm["crops"]:
                crop["cropId"] = str(crop.get("cropId", ""))
        farms.append(farm)

    # 3. Recent disease detections
    detections_cursor = (
        db.disease_detections.find({"farmerId": ObjectId(farmer_id)})
        .sort("detectedAt", -1)
        .limit(5)
    )
    recent_detections = []
    async for doc in detections_cursor:
        recent_detections.append({
            "id": str(doc["_id"]),
            "imageUrl": doc.get("imageUrl"),
            "detectedDisease": doc["detectedDisease"],
            "confidenceScore": doc["confidenceScore"],
            "detectedAt": doc["detectedAt"].isoformat(),
        })

    # 4. Weather (try to get for first farm's location or default city)
    weather_data = None
    try:
        weather_data = await get_current_weather("New Delhi")
    except Exception:
        pass

    # 5. Recent pest alerts
    pest_cursor = db.pest_alerts.find().sort("issuedAt", -1).limit(5)
    pest_alerts = []
    async for doc in pest_cursor:
        pest_alerts.append({
            "id": str(doc["_id"]),
            "region": doc["region"],
            "pestType": doc["pestType"],
            "severity": doc["severity"],
            "description": doc["description"],
            "issuedAt": doc["issuedAt"].isoformat(),
        })

    # 6. Recent notifications
    notif_cursor = (
        db.notifications.find({"farmerId": ObjectId(farmer_id)})
        .sort("createdAt", -1)
        .limit(10)
    )
    notifications = []
    async for doc in notif_cursor:
        notifications.append({
            "id": str(doc["_id"]),
            "type": doc["type"],
            "title": doc["title"],
            "message": doc["message"],
            "status": doc["status"],
            "createdAt": doc["createdAt"].isoformat(),
        })

    # 7. Irrigation reminders
    irrigation_reminders = []
    for farm in farms:
        for crop in farm.get("crops", []):
            schedule = crop.get("irrigationSchedule")
            if schedule:
                irrigation_reminders.append({
                    "farmName": farm["name"],
                    "cropType": crop["cropType"],
                    "frequency": schedule.get("frequency", "daily"),
                    "scheduledTime": schedule.get("scheduledTime", "06:00"),
                })

    return {
        "user": user_data,
        "farms": farms,
        "recentDetections": recent_detections,
        "weather": weather_data,
        "pestAlerts": pest_alerts,
        "irrigationReminders": irrigation_reminders,
        "notifications": notifications,
        "stats": {
            "totalFarms": len(farms),
            "totalCrops": sum(len(f.get("crops", [])) for f in farms),
            "totalDetections": await db.disease_detections.count_documents(
                {"farmerId": ObjectId(farmer_id)}
            ),
            "unreadNotifications": await db.notifications.count_documents(
                {"farmerId": ObjectId(farmer_id), "status": "pending"}
            ),
        },
    }

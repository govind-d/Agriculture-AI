"""
Pest alert routes.
"""

from fastapi import APIRouter, HTTPException, Depends, status
from datetime import datetime, timezone
from bson import ObjectId

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.schemas import PestAlertCreate, PestAlertSubscribe

router = APIRouter()


@router.get("/")
async def get_pest_alerts(
    region: str = "",
    limit: int = 20,
    user: dict = Depends(get_current_user),
):
    """Get pest alerts, optionally filtered by region."""
    db = get_db()

    query = {}
    if region:
        query["region"] = {"$regex": region, "$options": "i"}

    cursor = db.pest_alerts.find(query).sort("issuedAt", -1).limit(limit)

    alerts = []
    async for doc in cursor:
        alerts.append({
            "id": str(doc["_id"]),
            "region": doc["region"],
            "pestType": doc["pestType"],
            "severity": doc["severity"],
            "description": doc["description"],
            "issuedAt": doc["issuedAt"].isoformat(),
        })

    return {"alerts": alerts}


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_pest_alert(
    req: PestAlertCreate,
    user: dict = Depends(get_current_user),
):
    """Create a new pest alert (admin/expert only)."""
    if user.get("role") not in ("admin", "agri_expert"):
        raise HTTPException(
            status_code=403,
            detail="Only admins and agri-experts can create pest alerts.",
        )

    db = get_db()

    alert_doc = {
        "region": req.region,
        "pestType": req.pestType,
        "severity": req.severity.value,
        "description": req.description,
        "issuedAt": datetime.now(timezone.utc),
        "createdBy": ObjectId(user["_id"]) if isinstance(user["_id"], str) else user["_id"],
    }

    result = await db.pest_alerts.insert_one(alert_doc)

    return {
        "id": str(result.inserted_id),
        "message": "Pest alert created",
    }


@router.post("/subscribe")
async def subscribe_to_alerts(
    req: PestAlertSubscribe,
    user: dict = Depends(get_current_user),
):
    """Subscribe to pest alerts for specific regions."""
    db = get_db()
    user_id = ObjectId(user["_id"]) if isinstance(user["_id"], str) else user["_id"]

    # Add pest alert subscriptions to user
    await db.users.update_one(
        {"_id": user_id},
        {
            "$addToSet": {
                "alertSubscriptions": {
                    "$each": [
                        {"alertType": "pest", "region": r, "channelPreference": "push"}
                        for r in req.regions
                    ]
                }
            }
        },
    )

    return {"message": f"Subscribed to pest alerts for: {', '.join(req.regions)}"}

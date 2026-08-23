"""
Notification routes.
"""

from fastapi import APIRouter, HTTPException, Depends
from datetime import datetime, timezone
from bson import ObjectId

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.schemas import NotificationPreferences

router = APIRouter()


@router.get("/{farmer_id}")
async def get_notifications(
    farmer_id: str,
    limit: int = 50,
    unread_only: bool = False,
    user: dict = Depends(get_current_user),
):
    """Get notifications for a farmer."""
    db = get_db()

    query = {"farmerId": ObjectId(farmer_id)}
    if unread_only:
        query["status"] = "pending"

    cursor = (
        db.notifications.find(query)
        .sort("createdAt", -1)
        .limit(limit)
    )

    notifications = []
    async for doc in cursor:
        notifications.append({
            "id": str(doc["_id"]),
            "type": doc["type"],
            "title": doc["title"],
            "message": doc["message"],
            "channel": doc["channel"],
            "status": doc["status"],
            "createdAt": doc["createdAt"].isoformat(),
        })

    return {"notifications": notifications}


@router.post("/preferences")
async def update_preferences(
    req: NotificationPreferences,
    user: dict = Depends(get_current_user),
):
    """Update notification preferences for the current user."""
    db = get_db()
    user_id = ObjectId(user["_id"]) if isinstance(user["_id"], str) else user["_id"]

    await db.users.update_one(
        {"_id": user_id},
        {"$set": {"alertSubscriptions": req.alertSubscriptions}},
    )

    return {"message": "Notification preferences updated"}


@router.post("/{notification_id}/read")
async def mark_as_read(
    notification_id: str,
    user: dict = Depends(get_current_user),
):
    """Mark a notification as read/sent."""
    db = get_db()

    result = await db.notifications.update_one(
        {"_id": ObjectId(notification_id)},
        {"$set": {"status": "sent"}},
    )

    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Notification not found")

    return {"message": "Notification marked as read"}

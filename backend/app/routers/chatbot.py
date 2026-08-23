"""
AI Chatbot routes — Gemini-powered agriculture assistant.
"""

from fastapi import APIRouter, HTTPException, Depends
from datetime import datetime, timezone
from bson import ObjectId

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.schemas import ChatMessage
from app.services.chatbot_service import get_chatbot_response

router = APIRouter()


@router.post("/message")
async def send_message(
    req: ChatMessage,
    user: dict = Depends(get_current_user),
):
    """Send a message to the agriculture AI chatbot."""
    db = get_db()
    user_id = user["_id"] if isinstance(user["_id"], ObjectId) else ObjectId(user["_id"])

    # Get or create a chat session
    session = await db.chat_sessions.find_one(
        {"farmerId": user_id, "active": True}
    )

    if not session:
        session = {
            "farmerId": user_id,
            "messages": [],
            "active": True,
            "createdAt": datetime.now(timezone.utc),
        }
        result = await db.chat_sessions.insert_one(session)
        session["_id"] = result.inserted_id

    # Build chat history from session
    chat_history = session.get("messages", [])[-10:]

    # Get AI response
    response_text = get_chatbot_response(req.message, chat_history)

    # Save messages to session
    await db.chat_sessions.update_one(
        {"_id": session["_id"]},
        {
            "$push": {
                "messages": {
                    "$each": [
                        {"role": "user", "content": req.message, "timestamp": datetime.now(timezone.utc)},
                        {"role": "assistant", "content": response_text, "timestamp": datetime.now(timezone.utc)},
                    ]
                }
            }
        },
    )

    return {
        "response": response_text,
        "sessionId": str(session["_id"]),
    }


@router.get("/history")
async def get_chat_history(
    limit: int = 50,
    user: dict = Depends(get_current_user),
):
    """Get chat history for the current user."""
    db = get_db()
    user_id = user["_id"] if isinstance(user["_id"], ObjectId) else ObjectId(user["_id"])

    session = await db.chat_sessions.find_one(
        {"farmerId": user_id, "active": True}
    )

    if not session:
        return {"messages": [], "sessionId": None}

    messages = session.get("messages", [])[-limit:]

    # Serialize timestamps
    for msg in messages:
        if "timestamp" in msg:
            msg["timestamp"] = msg["timestamp"].isoformat()

    return {
        "messages": messages,
        "sessionId": str(session["_id"]),
    }


@router.post("/new-session")
async def start_new_session(user: dict = Depends(get_current_user)):
    """Start a new chat session (deactivates old one)."""
    db = get_db()
    user_id = user["_id"] if isinstance(user["_id"], ObjectId) else ObjectId(user["_id"])

    # Deactivate old sessions
    await db.chat_sessions.update_many(
        {"farmerId": user_id, "active": True},
        {"$set": {"active": False}},
    )

    return {"message": "New session started"}

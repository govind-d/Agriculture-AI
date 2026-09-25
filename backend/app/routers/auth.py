"""
Authentication routes — register, login, refresh.
"""

from fastapi import APIRouter, HTTPException, status
from datetime import datetime, timezone
from bson import ObjectId

from app.core.database import get_db
from app.core.security import (
    hash_password,
    verify_password,
    create_access_token,
    create_refresh_token,
    decode_token,
)
from app.models.schemas import RegisterRequest, LoginRequest, RefreshRequest

router = APIRouter()


def _phone_variants(phone: str) -> list[str]:
    """
    Forms an Indian mobile number may be stored in, canonical (+91XXXXXXXXXX) first.
    Lets "9000000000", "+91 90000-00000" and "09000000000" all match the same user,
    including older accounts stored without the +91 prefix.
    """
    digits = "".join(ch for ch in phone if ch.isdigit())
    if len(digits) == 12 and digits.startswith("91"):
        digits = digits[2:]
    elif len(digits) == 11 and digits.startswith("0"):
        digits = digits[1:]
    if len(digits) != 10:
        return [phone.strip()]
    return [f"+91{digits}", digits]


@router.post("/register", status_code=status.HTTP_201_CREATED)
async def register(req: RegisterRequest):
    """Register a new farmer/user."""
    db = get_db()

    # Check if phone already exists, in any of its written forms
    phone_variants = _phone_variants(req.phone)
    req.phone = phone_variants[0]
    existing = await db.users.find_one({"phone": {"$in": phone_variants}})
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="A user with this phone number already exists.",
        )

    # Check email uniqueness if provided
    if req.email:
        existing_email = await db.users.find_one({"email": req.email})
        if existing_email:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="A user with this email already exists.",
            )

    user_doc = {
        "name": req.name,
        "phone": req.phone,
        "email": req.email,
        "passwordHash": hash_password(req.password),
        "preferredLanguage": req.preferredLanguage,
        "role": req.role.value,
        "alertSubscriptions": [],
        "createdAt": datetime.now(timezone.utc),
    }

    result = await db.users.insert_one(user_doc)
    user_id = str(result.inserted_id)

    access_token = create_access_token(user_id, req.role.value)
    refresh_token = create_refresh_token(user_id)

    return {
        "accessToken": access_token,
        "refreshToken": refresh_token,
        "user": {
            "id": user_id,
            "name": req.name,
            "phone": req.phone,
            "email": req.email,
            "role": req.role.value,
        },
    }


@router.post("/login")
async def login(req: LoginRequest):
    """Login with phone + password."""
    db = get_db()

    user = await db.users.find_one({"phone": {"$in": _phone_variants(req.phone)}})
    if not user or not verify_password(req.password, user["passwordHash"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid phone number or password.",
        )

    user_id = str(user["_id"])
    access_token = create_access_token(user_id, user["role"])
    refresh_token = create_refresh_token(user_id)

    return {
        "accessToken": access_token,
        "refreshToken": refresh_token,
        "user": {
            "id": user_id,
            "name": user["name"],
            "phone": user["phone"],
            "email": user.get("email"),
            "role": user["role"],
        },
    }


@router.post("/refresh")
async def refresh_token(req: RefreshRequest):
    """Get a new access token using a refresh token."""
    payload = decode_token(req.refreshToken)

    if payload.get("type") != "refresh":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token type. Provide a refresh token.",
        )

    user_id = payload["sub"]

    # Verify user still exists
    db = get_db()
    user = await db.users.find_one({"_id": ObjectId(user_id)})
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found.",
        )

    access_token = create_access_token(user_id, user["role"])

    return {"accessToken": access_token}

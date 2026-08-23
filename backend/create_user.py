import asyncio
from datetime import datetime, timezone
import os
import sys

# Add the app directory to the path so we can import from app
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from motor.motor_asyncio import AsyncIOMotorClient
from app.core.security import hash_password
from app.core.config import settings

async def create_normal_user():
    # Use the URI from settings or default to localhost
    uri = settings.MONGODB_URI or "mongodb://localhost:27017"
    client = AsyncIOMotorClient(uri)
    db = client[settings.MONGODB_DB_NAME]
    
    phone = "+919876543210"
    password = "password123"
    
    # Check if user exists
    existing = await db.users.find_one({"phone": phone})
    if existing:
        print(f"User with phone {phone} already exists!")
        return
        
    user_doc = {
        "name": "Normal User",
        "phone": phone,
        "email": "user@example.com",
        "passwordHash": hash_password(password),
        "preferredLanguage": "en",
        "role": "farmer",
        "alertSubscriptions": [],
        "createdAt": datetime.now(timezone.utc),
    }
    
    await db.users.insert_one(user_doc)
    print(f"Successfully created user!\nPhone: {phone}\nPassword: {password}")

if __name__ == "__main__":
    try:
        asyncio.run(create_normal_user())
    except Exception as e:
        print(f"Error connecting to database. Is MongoDB running? ({e})")

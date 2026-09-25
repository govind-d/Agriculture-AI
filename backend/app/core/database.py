"""
MongoDB async connection using Motor.
"""

import certifi
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from app.core.config import settings

_client: AsyncIOMotorClient | None = None
_db: AsyncIOMotorDatabase | None = None


async def connect_db():
    """Connect to MongoDB Atlas (or local) on startup."""
    global _client, _db
    # Only use TLS CA file for Atlas (mongodb+srv) connections
    kwargs = {"serverSelectionTimeoutMS": 10000}
    if settings.MONGODB_URI.startswith("mongodb+srv"):
        kwargs["tlsCAFile"] = certifi.where()

    _client = AsyncIOMotorClient(settings.MONGODB_URI, **kwargs)
    _db = _client[settings.MONGODB_DB_NAME]

    # Create indexes — don't crash the app if Atlas is unreachable
    try:
        await _create_indexes()
        print(f"Connected to MongoDB: {settings.MONGODB_DB_NAME}")
    except Exception as e:
        print(f"[WARNING] MongoDB connection warning: {e}")
        print("   The app will start but DB operations may fail.")
        print("   Check: 1) Atlas IP whitelist  2) Credentials  3) Network")


async def close_db():
    """Close MongoDB connection on shutdown."""
    global _client
    if _client:
        _client.close()
        print("MongoDB connection closed")


def get_db() -> AsyncIOMotorDatabase:
    """Get the active database instance."""
    if _db is None:
        raise RuntimeError("Database not initialized. Call connect_db() first.")
    return _db


async def _create_indexes():
    """Create all required MongoDB indexes."""
    db = get_db()

    # Users — unique phone & email
    await db.users.create_index("phone", unique=True, sparse=True)
    await db.users.create_index("email", unique=True, sparse=True)

    # Farms — geospatial index
    await db.farms.create_index([("location", "2dsphere")])
    await db.farms.create_index("farmerId")

    # Disease detections — compound index for history queries
    await db.disease_detections.create_index(
        [("cropId", 1), ("detectedAt", -1)]
    )
    await db.disease_detections.create_index("farmerId")

    # Weather cache — TTL auto-delete
    await db.weather_cache.create_index("expiresAt", expireAfterSeconds=0)
    await db.weather_cache.create_index("locationKey", unique=True)

    # Crop price cache — TTL auto-delete
    await db.crop_price_cache.create_index("expiresAt", expireAfterSeconds=0)
    await db.crop_price_cache.create_index(
        [("cropType", 1), ("market", 1)], unique=True
    )

    # Market trends cache — TTL auto-delete
    await db.market_trends_cache.create_index("expiresAt", expireAfterSeconds=0)
    await db.market_trends_cache.create_index(
        [("cropType", 1), ("market", 1)], unique=True
    )

    # Pest alerts
    await db.pest_alerts.create_index("region")
    await db.pest_alerts.create_index("issuedAt")

    # Notifications
    await db.notifications.create_index(
        [("farmerId", 1), ("createdAt", -1)]
    )

    # Chat sessions
    await db.chat_sessions.create_index("farmerId")

    print("MongoDB indexes created")

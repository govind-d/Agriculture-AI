"""
AI Smart Agriculture Guardian — FastAPI Backend
Main application entry point.
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.core.database import connect_db, close_db
from app.routers import (
    auth,
    farms,
    disease,
    crops,
    fertilizer,
    weather,
    chatbot,
    prices,
    irrigation,
    pest_alerts,
    notifications,
    dashboard,
)


# ML models are now fully powered by Gemini API
ml_models = {}


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown events."""
    # Startup
    await connect_db()
    print("🚀 Agriculture Guardian API is ready (Serverless Mode)")
    yield
    # Shutdown
    await close_db()
    print("👋 Shutting down Agriculture Guardian API")


app = FastAPI(
    title="AI Smart Agriculture Guardian",
    description="AI-powered platform for Indian farmers — crop disease detection, "
    "weather alerts, crop recommendations, fertilizer guidance, and more.",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS — allow frontend origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routers
app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])
app.include_router(farms.router, prefix="/api/farms", tags=["Farms"])
app.include_router(disease.router, prefix="/api/disease-detection", tags=["Disease Detection"])
app.include_router(crops.router, prefix="/api/crops", tags=["Crop Recommendation"])
app.include_router(fertilizer.router, prefix="/api/fertilizer", tags=["Fertilizer Recommendation"])
app.include_router(weather.router, prefix="/api/weather", tags=["Weather"])
app.include_router(chatbot.router, prefix="/api/chatbot", tags=["AI Chatbot"])
app.include_router(prices.router, prefix="/api/crop-prices", tags=["Crop Prices"])
app.include_router(irrigation.router, prefix="/api/irrigation", tags=["Irrigation"])
app.include_router(pest_alerts.router, prefix="/api/pest-alerts", tags=["Pest Alerts"])
app.include_router(notifications.router, prefix="/api/notifications", tags=["Notifications"])
app.include_router(dashboard.router, prefix="/api/dashboard", tags=["Dashboard"])


@app.get("/", tags=["Health"])
async def root():
    return {
        "status": "healthy",
        "service": "AI Smart Agriculture Guardian",
        "version": "1.0.0",
        "models_loaded": {k: v is not None for k, v in ml_models.items()},
    }


@app.get("/health", tags=["Health"])
async def health_check():
    return {"status": "ok"}

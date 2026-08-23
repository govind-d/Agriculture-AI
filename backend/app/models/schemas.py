"""
Pydantic schemas for request/response validation.
"""

from pydantic import BaseModel, Field, EmailStr
from typing import Optional, List
from datetime import datetime
from enum import Enum


# ─── Enums ───────────────────────────────────────────────────────────────────

class UserRole(str, Enum):
    FARMER = "farmer"
    ADMIN = "admin"
    AGRI_EXPERT = "agri_expert"


class AlertType(str, Enum):
    WEATHER = "weather"
    PEST = "pest"
    PRICE = "price"
    EXTREME_WEATHER = "extreme_weather"
    IRRIGATION = "irrigation"


class ChannelPreference(str, Enum):
    PUSH = "push"
    SMS = "sms"
    EMAIL = "email"


class NotificationStatus(str, Enum):
    PENDING = "pending"
    SENT = "sent"
    FAILED = "failed"


class PestSeverity(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


# ─── Auth Schemas ────────────────────────────────────────────────────────────

class RegisterRequest(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)
    phone: str = Field(..., min_length=10, max_length=15)
    email: Optional[EmailStr] = None
    password: str = Field(..., min_length=6)
    preferredLanguage: str = Field(default="en")
    role: UserRole = Field(default=UserRole.FARMER)


class LoginRequest(BaseModel):
    phone: str
    password: str


class RefreshRequest(BaseModel):
    refreshToken: str


class AuthResponse(BaseModel):
    accessToken: str
    refreshToken: str
    user: dict


# ─── Farm Schemas ────────────────────────────────────────────────────────────

class GeoLocation(BaseModel):
    type: str = "Point"
    coordinates: List[float] = Field(..., min_length=2, max_length=2)


class IrrigationSchedule(BaseModel):
    frequency: str = Field(default="daily")
    scheduledTime: str = Field(default="06:00")
    lastNotifiedAt: Optional[datetime] = None


class CropCreate(BaseModel):
    cropType: str
    plantingDate: Optional[datetime] = None
    expectedHarvestDate: Optional[datetime] = None
    status: str = "active"
    irrigationSchedule: Optional[IrrigationSchedule] = None


class FarmCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=200)
    location: GeoLocation
    areaSize: float = Field(..., gt=0)
    soilType: str = ""
    crops: List[CropCreate] = []


class FarmUpdate(BaseModel):
    name: Optional[str] = None
    location: Optional[GeoLocation] = None
    areaSize: Optional[float] = None
    soilType: Optional[str] = None


# ─── Disease Detection Schemas ───────────────────────────────────────────────

class DiseaseDetectionResponse(BaseModel):
    id: str
    imageUrl: str
    detectedDisease: str
    confidenceScore: float
    lowConfidence: bool
    recommendedAction: str
    detectedAt: datetime


# ─── Crop Recommendation Schemas ─────────────────────────────────────────────

class CropRecommendationRequest(BaseModel):
    nitrogen: float = Field(..., ge=0, le=200)
    phosphorus: float = Field(..., ge=0, le=200)
    potassium: float = Field(..., ge=0, le=200)
    temperature: float = Field(..., ge=-10, le=60)
    humidity: float = Field(..., ge=0, le=100)
    ph: float = Field(..., ge=0, le=14)
    rainfall: float = Field(..., ge=0, le=500)


class CropRecommendationResponse(BaseModel):
    topCrops: List[dict]
    featureImportance: dict
    insight: str
    warnings: List[str] = []


# ─── Fertilizer Recommendation Schemas ───────────────────────────────────────

class FertilizerRecommendationRequest(BaseModel):
    temperature: float = Field(..., ge=0, le=50)
    humidity: float = Field(..., ge=0, le=100)
    moisture: float = Field(..., ge=0, le=100)
    soilType: str
    cropType: str
    nitrogen: float = Field(..., ge=0, le=200)
    phosphorus: float = Field(..., ge=0, le=200)
    potassium: float = Field(..., ge=0, le=200)
    landArea: float = Field(..., gt=0)


class FertilizerRecommendationResponse(BaseModel):
    fertilizer: str
    qtyPerAcre: float
    totalQty: float
    explanation: str
    warnings: List[str] = []


# ─── Weather Schemas ─────────────────────────────────────────────────────────

class WeatherResponse(BaseModel):
    city: str
    temperature: float
    humidity: float
    description: str
    windSpeed: float
    advice: List[str] = []


# ─── Chatbot Schemas ─────────────────────────────────────────────────────────

class ChatMessage(BaseModel):
    message: str = Field(..., min_length=1, max_length=2000)


class ChatResponse(BaseModel):
    response: str
    sessionId: str


# ─── Crop Prices Schemas ─────────────────────────────────────────────────────

class CropPriceResponse(BaseModel):
    cropType: str
    market: str
    price: float
    unit: str
    priceDate: str


# ─── Pest Alert Schemas ──────────────────────────────────────────────────────

class PestAlertCreate(BaseModel):
    region: str
    pestType: str
    severity: PestSeverity
    description: str


class PestAlertSubscribe(BaseModel):
    regions: List[str]


# ─── Notification Schemas ────────────────────────────────────────────────────

class NotificationPreferences(BaseModel):
    alertSubscriptions: List[dict]


# ─── Dashboard Schemas ───────────────────────────────────────────────────────

class DashboardResponse(BaseModel):
    user: dict
    farms: List[dict]
    recentDetections: List[dict] = []
    weather: Optional[dict] = None
    pestAlerts: List[dict] = []
    irrigationReminders: List[dict] = []
    cropPrices: List[dict] = []
    notifications: List[dict] = []

# AI Smart Agriculture Guardian — Implementation Plan

> Reference doc for AI coding agents (Claude Code, Cursor, etc.) implementing this project.
> Work through the checklists in order. Check items off as they're completed. Ask a human
> before making a call marked **[DECISION NEEDED]**.

## 1. Overview

A Java/Spring Boot web app that gives farmers: crop disease identification from a photo,
weather-based alerts, irrigation reminders, pest alerts, crop price info, extreme weather
notifications, and a single dashboard tying it together. Target market: India (weather/price
integrations assume IMD/OpenWeatherMap and Agmarknet/data.gov.in).

## 2. Tech Stack

| Layer | Choice | Notes |
|---|---|---|
| Backend | Java 21, Spring Boot 3.x | REST API |
| Database | **MongoDB Atlas** | Spring Data MongoDB, not JPA |
| Cache | MongoDB TTL-indexed collections | For weather/price cache — no Redis needed for this. Add Redis later only if session/rate-limit needs justify it |
| Object storage | **Cloudinary** | Disease-detection photo uploads. Alt: Firebase Storage |
| Messaging | RabbitMQ | Async notification delivery |
| ML inference | Python microservice (FastAPI + TF/PyTorch) | Called internally via REST. See §6 |
| Notifications | Firebase Cloud Messaging (push), MSG91/Twilio (SMS), JavaMailSender (email) | SMS is first-class, not fallback |
| Auth | Spring Security + JWT | Access + refresh tokens |
| Frontend | React, PWA-installable | Mobile-first, low-bandwidth conscious |
| Scheduling | Spring Scheduler / Quartz | Irrigation reminders, weather/price polling |
| Deploy | Docker + GitHub Actions | Cloud-agnostic now that Atlas handles the DB — Render/Railway/GCP/Azure/AWS all work |

No AWS dependency anywhere in this stack.

## 3. Architecture

```
Client (React SPA/PWA)
   |
Spring Boot REST API (Spring Security/JWT)
   |
   +-- Auth & Farmer Service
   +-- Disease Detection Service ---- Cloudinary (images) + ML microservice (inference)
   +-- Weather Service -------------- IMD/OpenWeatherMap API, cached in weather_cache (TTL)
   +-- Crop Price Service ----------- Agmarknet/data.gov.in API, cached in crop_price_cache (TTL)
   +-- Irrigation Scheduler --------- Spring Scheduler/Quartz jobs
   +-- Pest Alert Service
   +-- Notification Service --------- RabbitMQ consumer -> FCM / SMS / email
   +-- Dashboard Aggregator --------- fan-out read across the above, composed response
   |
MongoDB Atlas (all collections below)
```

Modular monolith: each service is a separate package with its own MongoDB collection(s),
deployed as one Spring Boot app. Clean boundaries now make a later microservices split
possible without a rewrite.

**[DECISION NEEDED]** ML serving: Python microservice (recommended — access to the mature
plant-disease-classification tooling) vs. in-JVM DL4J/ONNX Runtime (single-runtime deploy,
smaller ecosystem). Default to the Python microservice unless told otherwise.

## 4. Data Model — MongoDB Collections

MongoDB is schema-flexible; the shapes below are the intended structure. Embed data that's
always read together (crops inside a farm); keep independently-queried, growing data
(detections, notifications) as separate collections.

### `users`
```json
{
  "_id": "ObjectId",
  "name": "string",
  "phone": "string",
  "email": "string",
  "passwordHash": "string",
  "preferredLanguage": "string",
  "role": "farmer | admin | agri_expert",
  "alertSubscriptions": [
    { "alertType": "weather | pest | price | extreme_weather", "channelPreference": "push | sms | email" }
  ],
  "createdAt": "date"
}
```

### `farms`
```json
{
  "_id": "ObjectId",
  "farmerId": "ObjectId (ref users)",
  "name": "string",
  "location": { "type": "Point", "coordinates": ["lng", "lat"] },
  "areaSize": "number",
  "soilType": "string",
  "crops": [
    {
      "cropId": "ObjectId",
      "cropType": "string",
      "plantingDate": "date",
      "expectedHarvestDate": "date",
      "status": "string",
      "irrigationSchedule": { "frequency": "string", "scheduledTime": "string", "lastNotifiedAt": "date" }
    }
  ]
}
```
Index: `2dsphere` on `location` (enables future proximity queries, e.g. regional pest alerts).

### `disease_detections`
```json
{
  "_id": "ObjectId",
  "farmerId": "ObjectId",
  "farmId": "ObjectId",
  "cropId": "ObjectId",
  "imageUrl": "string (Cloudinary URL)",
  "detectedDisease": "string",
  "confidenceScore": "number",
  "recommendedAction": "string",
  "detectedAt": "date"
}
```
Index: compound on `{ cropId: 1, detectedAt: -1 }` for history queries.

### `weather_cache`
```json
{ "_id": "ObjectId", "locationKey": "string", "forecastJson": "object", "fetchedAt": "date", "expiresAt": "date" }
```
TTL index on `expiresAt` (`expireAfterSeconds: 0`) — Mongo auto-deletes stale entries.

### `crop_price_cache`
```json
{ "_id": "ObjectId", "cropType": "string", "market": "string", "price": "number", "unit": "string", "priceDate": "date", "expiresAt": "date" }
```
TTL index on `expiresAt` (set ~24h out; these sources refresh daily).

### `pest_alerts`
```json
{ "_id": "ObjectId", "region": "string", "pestType": "string", "severity": "low | medium | high", "description": "string", "issuedAt": "date" }
```

### `notifications`
```json
{ "_id": "ObjectId", "farmerId": "ObjectId", "type": "string", "title": "string", "message": "string", "channel": "push | sms | email", "status": "pending | sent | failed", "createdAt": "date" }
```
Index: `{ farmerId: 1, createdAt: -1 }`.

## 5. API Endpoints

REST, versioned under `/api`, JSON, JWT bearer auth except register/login.

**Auth & Farmer**
- `POST /api/auth/register`
- `POST /api/auth/login`
- `GET /api/farmers/{id}`
- `POST /api/farmers/{id}/farms`

**Disease Detection**
- `POST /api/disease-detection/analyze` — multipart image → Cloudinary upload → ML call → result
- `GET /api/disease-detection/history/{cropId}`

**Weather / Price / Pest**
- `GET /api/weather/current?farmId=`
- `GET /api/weather/forecast?farmId=`
- `GET /api/crop-prices?crop=&market=`
- `GET /api/crop-prices/trends?crop=`
- `GET /api/pest-alerts?region=`
- `POST /api/pest-alerts/subscribe`

**Irrigation / Notifications / Dashboard**
- `GET /api/irrigation/schedule/{farmId}`
- `POST /api/irrigation/schedule`
- `GET /api/notifications/{farmerId}`
- `POST /api/notifications/preferences`
- `GET /api/dashboard/{farmerId}` — aggregated payload

## 6. ML Pipeline (Disease Detection)

- Start from a public dataset (e.g. PlantVillage) for the priority crops.
- Transfer learning on a lightweight backbone (MobileNetV3 / EfficientNet-Lite).
- Train/evaluate in Python; serve via FastAPI, called internally by the Spring Boot backend.
- Return a confidence score with every prediction. Below ~60%, the API should return a
  `lowConfidence: true` flag rather than a bare guess — the UI shows "consult a local
  agri-expert" instead of a false-confident diagnosis.

## 7. Conventions

- Package structure: `com.agriguardian.{auth,farm,disease,weather,price,irrigation,pest,notification,dashboard}`
- Each package: `controller/`, `service/`, `repository/` (Spring Data MongoDB `MongoRepository`)
- Collection/field naming: camelCase (Mongo/JS convention), collection names lowercase snake_case per §4
- Config via environment variables (see §9), never committed

## 8. Implementation Checklist

### Phase 0 — Setup
- [ ] Init Spring Boot project (Java 21) with Web, Security, Spring Data MongoDB
- [ ] Provision MongoDB Atlas cluster (free M0 for dev), configure connection string
- [ ] Create Cloudinary account, add SDK dependency, verify test upload
- [ ] Docker Compose for local dev (backend + local Mongo fallback for offline dev)
- [ ] GitHub Actions skeleton: build + test on push

### Phase 1 — Core Farmer Module
- [ ] `users` document/repository + register/login (JWT issue + refresh)
- [ ] `farms` document/repository + CRUD, embedded `crops` handling
- [ ] `2dsphere` index on farm location
- [ ] Dashboard endpoint skeleton (returns farm + profile, no aggregation yet)

### Phase 2 — Disease Detection
- [ ] Image upload endpoint → Cloudinary → store returned URL
- [ ] ML microservice: stand up FastAPI stub, wire internal call from backend
- [ ] `disease_detections` collection + history endpoint
- [ ] Confidence threshold + low-confidence response handling

### Phase 3 — Weather & Price
- [ ] Weather API integration (IMD/OpenWeatherMap)
- [ ] `weather_cache` with TTL index
- [ ] Crop price API integration (Agmarknet/data.gov.in)
- [ ] `crop_price_cache` with TTL index
- [ ] Alert threshold logic (configurable per crop type, not hardcoded)

### Phase 4 — Irrigation & Pest Alerts
- [ ] Irrigation reminder scheduler job (reads embedded `irrigationSchedule`)
- [ ] `pest_alerts` collection + subscribe endpoint
- [ ] Notification service: RabbitMQ consumer → FCM + SMS integration

### Phase 5 — Extreme Weather & Dashboard Polish
- [ ] Severe-weather notification channel (higher priority than routine weather alerts)
- [ ] Full dashboard aggregation (fan-out across all services, cached short TTL)
- [ ] Notification preferences endpoint wired to `alertSubscriptions`

### Phase 6 — Testing
- [ ] Unit tests: JUnit 5 + Mockito
- [ ] Integration tests: Testcontainers (MongoDB module)
- [ ] ML evaluation: accuracy/precision/recall on held-out set before promoting a model version
- [ ] Load test dashboard + disease-detection endpoints (k6/Gatling)

### Phase 7 — Deploy
- [ ] Production Atlas cluster (paid tier, backups on)
- [ ] Deploy backend + ML service (any cloud — no longer AWS-locked)
- [ ] Final docs, env var checklist, demo

## 9. Environment Variables

```
MONGODB_URI=
JWT_SECRET=
CLOUDINARY_URL=
WEATHER_API_KEY=
CROP_PRICE_API_KEY=
FCM_SERVER_KEY=
SMS_API_KEY=
ML_SERVICE_URL=
```

## 10. Open Decisions

- ML serving approach (§3) — default: Python microservice
- Whether to add Redis later for session/dashboard caching, or stay Mongo-only
- Multilingual UI scope: MVP or Phase 2
- Pest alert data source: on-platform aggregated signals only, or an external agri-extension feed

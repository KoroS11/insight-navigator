# NSA-X ML Integration Guide

> **For:** ML Engineer integrating machine learning models  
> **Project:** Neuro-Symbolic Autonomous Security Analyst  
> **Last Updated:** March 14, 2026

---

## Table of Contents

1. [Project Overview](#project-overview)
2. [Architecture Summary](#architecture-summary)
3. [Backend Status](#backend-status)
4. [Frontend Status](#frontend-status)
5. [ML Integration Points](#ml-integration-points)
6. [Data Flow](#data-flow)
7. [Getting Started](#getting-started)
8. [API Reference](#api-reference)
9. [Testing](#testing)
10. [Considerations & Best Practices](#considerations--best-practices)

---

## Project Overview

NSA-X is a **7-layer security analytics pipeline** that combines:
- **Neural detection** (ML-based anomaly scoring) ← **YOUR WORK**
- **Symbolic reasoning** (rule-based logic)
- **Explainability engine** (human-readable explanations)

The system ingests security events, processes them through the pipeline, generates alerts with risk scores, and allows analysts to make decisions.

### Tech Stack

| Component | Technology |
|-----------|------------|
| Backend | FastAPI + Python 3.12 |
| Database | SQLite (dev) / PostgreSQL (prod) |
| ORM | SQLAlchemy (async) |
| Auth | JWT (OAuth2 password flow) |
| Frontend | React + TypeScript + Vite |
| UI | shadcn/ui + Tailwind CSS |
| State | TanStack Query (React Query) |

---

## Architecture Summary

```
┌─────────────────────────────────────────────────────────────────────┐
│                        NSA-X Pipeline                                │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  Layer 1: Data Ingestion                                            │
│  └─ Raw security events (network logs, auth events, etc.)           │
│                           ↓                                          │
│  Layer 2: Event Processing                                          │
│  └─ Normalization, enrichment, field extraction                     │
│                           ↓                                          │
│  Layer 3: Neural Detection  ← ★ YOUR INTEGRATION POINT ★            │
│  └─ Anomaly scores, behavioral analysis, pattern detection          │
│                           ↓                                          │
│  Layer 4: Symbolic Reasoning                                        │
│  └─ Rule evaluation, policy matching                                │
│                           ↓                                          │
│  Layer 5: Reasoning Integration                                     │
│  └─ Risk score fusion, alert generation                             │
│                           ↓                                          │
│  Layer 6: Explainability Engine                                     │
│  └─ Natural language explanations, evidence trees                   │
│                           ↓                                          │
│  Layer 7: Analyst Decision                                          │
│  └─ Human-in-the-loop decisions, audit trail                        │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
```

---

## Backend Status

### ✅ Fully Implemented & Tested

| Layer | Service | File | Status |
|-------|---------|------|--------|
| 1 | Data Ingestion | `app/services/layer1_ingestion.py` | ✅ Complete |
| 2 | Event Processing | `app/services/layer2_processing.py` | ✅ Complete |
| 3 | Neural Detection | `app/services/layer3_neural.py` | ⚠️ **Mock (needs ML)** |
| 4 | Symbolic Reasoning | `app/services/layer4_symbolic.py` | ✅ Complete |
| 5 | Integration | `app/services/layer5_integration.py` | ✅ Complete |
| 6 | Explainability | `app/services/layer6_explainability.py` | ✅ Complete |
| 7 | Decisions | `app/services/layer7_decisions.py` | ✅ Complete |
| - | Pipeline Orchestrator | `app/services/pipeline.py` | ✅ Complete |

### Test Coverage

```
Tests: 192 passing
Coverage: 87%
```

### API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/auth/token` | Login (OAuth2 password) |
| POST | `/api/v1/auth/refresh` | Refresh token |
| GET | `/api/v1/auth/me` | Get current user |
| POST | `/api/v1/events/` | Ingest event (triggers full pipeline) |
| GET | `/api/v1/events/` | List events |
| GET | `/api/v1/events/{id}` | Get event details |
| GET | `/api/v1/events/{id}/processed` | Get processed event |
| GET | `/api/v1/alerts/` | List alerts |
| GET | `/api/v1/alerts/{id}` | Get alert with full context |
| PATCH | `/api/v1/alerts/{id}/status` | Update alert status |
| POST | `/api/v1/alerts/{id}/decisions` | Submit analyst decision |
| GET | `/api/v1/alerts/{id}/explanation` | Get explanation |
| GET | `/api/v1/system/health` | Health check |
| GET | `/api/v1/system/rules` | List security rules |
| GET | `/api/v1/audit/` | Audit log |

---

## Frontend Status

### ✅ Working Features

| Feature | Status | Notes |
|---------|--------|-------|
| Login/Logout | ✅ | JWT auth, token persistence |
| Dashboard | ✅ | Alert list, metrics, 5s polling |
| Alert Detail | ✅ | Full context, explanation, decisions |
| Decision Actions | ✅ | ESCALATE, DISMISS, MARK_SAFE, WATCH |
| Status Bar | ✅ | Live health, pending count |
| Governance | ✅ | Audit trail (live data) |
| Architecture | ⚠️ | Static diagram (placeholder) |

### Pages

| Route | Component | Description |
|-------|-----------|-------------|
| `/login` | `Login.tsx` | Authentication |
| `/` | `Index.tsx` | Dashboard with alerts |
| `/alerts/:id` | `AlertDetail.tsx` | Alert analysis + decisions |
| `/architecture` | `Architecture.tsx` | System diagram |
| `/governance` | `Governance.tsx` | Audit trail + policies |

---

## ML Integration Points

### Primary Integration: Layer 3 Neural Detection

**File:** `backend/app/services/layer3_neural.py`

This is where your ML models plug in. The current implementation uses **mock heuristics** that you'll replace with real models.

#### Current Mock Implementation

```python
class NeuralDetectionService:
    async def analyze(self, processed_event: ProcessedEvent) -> NeuralDetection:
        """
        Analyze a processed event and generate neural detection scores.
        
        Input: ProcessedEvent with normalized fields
        Output: NeuralDetection with scores between 0.0 and 1.0
        """
        # CURRENT: Simple heuristics (REPLACE WITH ML)
        anomaly_score = self._calculate_anomaly_score(processed_event)
        frequency_score = self._calculate_frequency_score(processed_event)
        port_score = self._calculate_port_score(processed_event)
        temporal_score = self._calculate_temporal_score(processed_event)
        geographic_score = self._calculate_geographic_score(processed_event)
        
        return NeuralDetection(
            processed_event_id=processed_event.id,
            anomaly_score=anomaly_score,
            frequency_score=frequency_score,
            port_score=port_score,
            temporal_score=temporal_score,
            geographic_score=geographic_score,
            model_version="heuristic-v1",  # Update to your model version
        )
```

#### What Each Score Means

| Score | Range | Purpose | Suggested ML Approach |
|-------|-------|---------|----------------------|
| `anomaly_score` | 0.0-1.0 | Overall anomaly detection | Isolation Forest, Autoencoder, One-Class SVM |
| `frequency_score` | 0.0-1.0 | Unusual access frequency | Time-series models, ARIMA, Prophet |
| `port_score` | 0.0-1.0 | Unusual port usage | Classification on port patterns |
| `temporal_score` | 0.0-1.0 | Unusual timing | Time-based behavioral models |
| `geographic_score` | 0.0-1.0 | Unusual geo location | GeoIP + behavioral baseline |

#### Input Data Available

The `ProcessedEvent` object gives you:

```python
processed_event.parsed_fields = {
    "network": {
        "source": {"ip": "192.168.1.100", "port": 54321},
        "destination": {"ip": "10.0.0.50", "port": 443},
        "protocol": "TCP"
    },
    "temporal": {
        "timestamp": "2026-01-17T12:30:00Z",
        "hour_of_day": 12,
        "day_of_week": 4,  # Friday
        "is_business_hours": True
    },
    "asset": {
        "hostname": "workstation-042",
        "criticality": 75  # 1-100 scale
    }
}
```

#### Your Implementation

Replace the mock methods with your ML inference:

```python
import logging
import joblib
import numpy as np

logger = logging.getLogger(__name__)


class NeuralDetectionService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.anomaly_model = None
        self.frequency_model = None

        # Load your models once at startup.
        try:
            self.anomaly_model = joblib.load("models/anomaly_detector.pkl")
            self.frequency_model = joblib.load("models/frequency_analyzer.pkl")
        except Exception as exc:
            logger.exception("Failed to load ML models in NeuralDetectionService.__init__: %s", exc)
            raise RuntimeError("ML model loading failed") from exc

    def _extract_features(self, processed_event: ProcessedEvent) -> np.ndarray:
        """
        Convert parsed_fields into model-ready features.
        Replace this stub with your actual feature engineering.
        """
        parsed = processed_event.parsed_fields or {}
        temporal = parsed.get("temporal", {})
        network = parsed.get("network", {})
        dest = network.get("destination", {})

        hour = float(temporal.get("hour_of_day", 0))
        day = float(temporal.get("day_of_week", 0))
        dest_port = float(dest.get("port") or 0)
        criticality = float(parsed.get("asset", {}).get("criticality", 50))

        # Shape as 2D array for sklearn-style estimators.
        return np.array([[hour, day, dest_port, criticality]], dtype=np.float32)

    def _score_model(self, model, features: np.ndarray) -> float:
        """
        Model API handling:
        - Prefer model.predict_proba(features)
        - Fallback to model.predict(features)
        - Clamp result to [0.0, 1.0]
        """
        if hasattr(model, "predict_proba"):
            proba = model.predict_proba(features)
            # Binary classifiers often return [[p_neg, p_pos]]
            score = float(proba[0][-1])
        else:
            pred = model.predict(features)
            score = float(pred[0])

        return max(0.0, min(1.0, score))

    async def analyze(self, processed_event: ProcessedEvent) -> NeuralDetection:
        """
        Main inference path with explicit error handling.
        """
        try:
            features = self._extract_features(processed_event)

            anomaly_score = self._score_model(self.anomaly_model, features)
            frequency_score = self._score_model(self.frequency_model, features)
            port_score = 0.5
            temporal_score = 0.5
            geographic_score = 0.5
        except Exception as exc:
            logger.exception("Inference failed in NeuralDetectionService.analyze: %s", exc)
            raise RuntimeError("ML inference failed") from exc

        return NeuralDetection(
            processed_event_id=processed_event.id,
            anomaly_score=anomaly_score,
            frequency_score=frequency_score,
            port_score=port_score,
            temporal_score=temporal_score,
            geographic_score=geographic_score,
            model_version="your-model-v1.0",
        )
```

---

## Data Flow

### Event Processing Pipeline

```
1. Event Ingested (POST /api/v1/events/)
   │
   ├── Layer 1: Store raw event
   │   └── Event record created
   │
   ├── Layer 2: Process & enrich
   │   └── ProcessedEvent with normalized fields
   │
   ├── Layer 3: Neural analysis  ← YOUR CODE RUNS HERE
   │   └── NeuralDetection with 5 scores
   │
   ├── Layer 4: Rule evaluation
   │   └── List of matched rules + severities
   │
   ├── Layer 5: Risk fusion
   │   └── Alert created with composite_risk_score
   │
   ├── Layer 6: Generate explanation
   │   └── Natural language + evidence tree
   │
   └── Layer 7: Await analyst decision
       └── Human reviews and decides
```

### Database Schema (Relevant Tables)

```sql
-- Your ML output goes here
CREATE TABLE neural_detections (
    id UUID PRIMARY KEY,
    processed_event_id UUID REFERENCES processed_events(id),
    anomaly_score DECIMAL(3,2) CHECK (0 <= anomaly_score <= 1),
    frequency_score DECIMAL(3,2) CHECK (0 <= frequency_score <= 1),
    port_score DECIMAL(3,2) CHECK (0 <= port_score <= 1),
    temporal_score DECIMAL(3,2) CHECK (0 <= temporal_score <= 1),
    geographic_score DECIMAL(3,2) CHECK (0 <= geographic_score <= 1),
    detection_timestamp TIMESTAMP,
    model_version VARCHAR(50)  -- Track which model version produced this
);

-- Input for your ML
CREATE TABLE processed_events (
    id UUID PRIMARY KEY,
    event_id UUID REFERENCES events(id),
    parsed_fields JSONB,  -- Normalized event data
    asset_hostname VARCHAR(255),
    asset_criticality INTEGER,
    event_hash VARCHAR(64),
    processing_timestamp TIMESTAMP
);
```

---

## Getting Started

### 1. Clone & Setup

```bash
# Clone the repo
git clone <repo-url>
cd insight-navigator

# Backend setup
cd backend
python -m venv venv
venv\Scripts\activate  # Windows
pip install -r requirements.txt

# Create .env file
cp .env.example .env
# Edit .env with your settings

# Run backend
uvicorn app.main:app --reload
```

### 2. Verify Backend

```bash
# Health check
curl http://localhost:8000/api/v1/system/health

# API docs
open http://localhost:8000/docs
```

### 3. Frontend (optional for ML work)

```bash
cd ..  # Back to root
npm install
npm run dev
# Open http://localhost:8080/insight-navigator/
```

### 4. Run Tests

```bash
cd backend
pytest --tb=short
pytest tests/test_layer3_neural.py -v  # Just neural tests
```

---

## API Reference

### Ingest Event (Triggers Full Pipeline)

```bash
# Login first
TOKEN=$(curl -s -X POST http://localhost:8000/api/v1/auth/token \
  -d "username=admin&password=admin123&grant_type=password" \
  -H "Content-Type: application/x-www-form-urlencoded" | jq -r .access_token)

# Ingest event
curl -X POST http://localhost:8000/api/v1/events/ \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "event_type": "network_connection",
    "source_ip": "192.168.1.100",
    "dest_ip": "10.0.0.50",
    "dest_port": 443,
    "protocol": "TCP",
    "timestamp": "2026-01-17T12:30:00Z",
    "raw_data": {
      "bytes_sent": 1500,
      "bytes_received": 3200,
      "duration_ms": 450
    }
  }'
```

### Response (Pipeline Result)

```json
{
  "event_id": "uuid",
  "processed_event_id": "uuid",
  "anomaly_score": 0.72,      // From YOUR model
  "rules_matched": ["RULE-001", "RULE-003"],
  "alert_id": "uuid",
  "risk_score": 78,
  "classification": "HIGH",
  "status": "success"
}
```

---

## Testing

### Run All Tests

```bash
cd backend
pytest
```

### Run Layer 3 Tests Only

```bash
pytest tests/test_layer3_neural.py -v
```

### Test Your ML Integration

Create a test file `tests/test_ml_integration.py`:

```python
import pytest
from app.services.layer3_neural import NeuralDetectionService

@pytest.mark.asyncio
async def test_your_model_produces_valid_scores(db_session, sample_processed_event):
    service = NeuralDetectionService(db_session)
    result = await service.analyze(sample_processed_event)
    
    # All scores must be between 0 and 1
    assert 0.0 <= result.anomaly_score <= 1.0
    assert 0.0 <= result.frequency_score <= 1.0
    assert 0.0 <= result.port_score <= 1.0
    assert 0.0 <= result.temporal_score <= 1.0
    assert 0.0 <= result.geographic_score <= 1.0
    
    # Model version should be set
    assert result.model_version is not None
```

---

## Considerations & Best Practices

### 1. Model Versioning

Always set `model_version` in your NeuralDetection output:
```python
model_version="anomaly-detector-v2.3.1"
```

This is stored in the database and shown in the UI for explainability.

### 2. Score Calibration

Scores should be **calibrated probabilities** (0.0-1.0):
- `0.0` = Completely normal
- `0.5` = Uncertain / borderline
- `1.0` = Highly anomalous

The downstream layers use these scores to compute `composite_risk_score`.

### 3. Inference Speed

The pipeline runs synchronously per event. Keep inference fast:
- Target: < 100ms per event
- Load models once at service initialization
- Use batch inference if processing multiple events

### 4. Feature Engineering

The `ProcessedEvent` provides normalized data. You may want to:
- Add historical features (rolling averages, baselines)
- Add entity embeddings (IP reputation, user behavior)
- Add graph features (connection patterns)

### 5. Model Persistence

Store models in `backend/models/` or use a model registry. Example structure:
```
backend/
├── models/
│   ├── anomaly_detector_v1.pkl
│   ├── frequency_analyzer_v1.pkl
│   └── config.yaml
└── app/
    └── services/
        └── layer3_neural.py  # Loads models from ../models/
```

### 6. Async Considerations

The service uses async SQLAlchemy. If your ML inference is CPU-bound:
```python
import asyncio
from concurrent.futures import ThreadPoolExecutor

executor = ThreadPoolExecutor(max_workers=4)

async def analyze(self, processed_event):
    # Run CPU-bound inference in thread pool
    loop = asyncio.get_event_loop()
    scores = await loop.run_in_executor(
        executor, 
        self._sync_inference, 
        processed_event
    )
    return NeuralDetection(**scores)
```

### 7. Handling Missing Data

Events may have missing fields. Handle gracefully:
```python
port = processed_event.parsed_fields.get("network", {}).get("destination", {}).get("port")
if port is None:
    port_score = 0.5  # Neutral score for missing data
```

### 8. Explainability

The Layer 6 explainability engine generates explanations. To improve them:
- Consider adding feature importance to your model output
- Add confidence intervals if available
- Document what each score component means

---

## File Structure Reference

```
backend/
├── app/
│   ├── core/
│   │   ├── config.py          # Environment settings
│   │   ├── database.py        # SQLAlchemy setup
│   │   └── security.py        # JWT auth
│   ├── models/
│   │   └── __init__.py        # SQLAlchemy models
│   ├── routers/
│   │   ├── alerts.py          # Alert endpoints
│   │   ├── auth.py            # Auth endpoints
│   │   ├── events.py          # Event endpoints
│   │   └── system.py          # Health, rules
│   ├── schemas/
│   │   └── __init__.py        # Pydantic schemas
│   ├── services/
│   │   ├── layer1_ingestion.py
│   │   ├── layer2_processing.py
│   │   ├── layer3_neural.py   # ★ YOUR MAIN FILE ★
│   │   ├── layer4_symbolic.py
│   │   ├── layer5_integration.py
│   │   ├── layer6_explainability.py
│   │   ├── layer7_decisions.py
│   │   └── pipeline.py        # Orchestrator
│   └── main.py                # FastAPI app
├── tests/
│   ├── test_layer3_neural.py  # Neural tests
│   └── ...
├── .env.example
├── requirements.txt
└── pytest.ini
```

---

## Contact & Support

If you have questions about:
- **Backend architecture**: Check `backend/README.md`
- **API contracts**: Visit `http://localhost:8000/docs`
- **Frontend**: Check `src/` directory

---

**Good luck with the ML integration!** 🚀

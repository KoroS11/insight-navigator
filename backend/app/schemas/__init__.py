"""
NSA-X API Schemas
Pydantic models for request/response validation
"""
import uuid
from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel, Field, IPvAnyAddress, field_validator, model_validator


# =============================================================================
# Authentication Schemas
# =============================================================================

class LoginRequest(BaseModel):
    """Login request body."""
    username: str = Field(..., min_length=1, max_length=100)
    password: str = Field(..., min_length=1)


class TokenResponse(BaseModel):
    """Token response."""
    access_token: str
    token_type: str = "bearer"
    expires_in: int


class UserResponse(BaseModel):
    """User information response."""
    id: uuid.UUID
    username: str
    full_name: Optional[str] = None
    role: str
    is_active: bool
    created_at: datetime
    last_login: Optional[datetime] = None

    class Config:
        from_attributes = True


# =============================================================================
# Layer 1: Event Ingestion Schemas
# =============================================================================

class EventIngestRequest(BaseModel):
    """Event ingestion request - Layer 1."""
    timestamp: datetime
    source_ip: str
    dest_ip: str
    source_port: Optional[int] = Field(None, ge=0, le=65535)
    dest_port: Optional[int] = Field(None, ge=0, le=65535)
    protocol: str = Field(..., max_length=10)
    event_type: str = Field(..., min_length=1, max_length=50)
    raw_data: dict[str, Any]

    @field_validator("source_ip", "dest_ip")
    @classmethod
    def validate_ip(cls, v: str) -> str:
        """Validate IP address format."""
        try:
            IPvAnyAddress(v)
            return v
        except ValueError:
            raise ValueError(f"Invalid IP address: {v}")

    @field_validator("protocol")
    @classmethod
    def validate_protocol(cls, v: str) -> str:
        """Validate protocol is in allowed list."""
        allowed = {"TCP", "UDP", "ICMP", "HTTP", "HTTPS", "DNS", "SSH", "FTP", "SMTP"}
        v_upper = v.upper()
        if v_upper not in allowed:
            raise ValueError(f"Protocol must be one of: {', '.join(allowed)}")
        return v_upper


# Alias for backwards compatibility
EventCreate = EventIngestRequest


class EventIngestResponse(BaseModel):
    """Event ingestion success response."""
    event_id: uuid.UUID
    status: str = "ingested"
    timestamp: datetime


class PipelineResultResponse(BaseModel):
    """Result of full pipeline processing."""
    event_id: uuid.UUID
    processed_event_id: Optional[uuid.UUID] = None
    anomaly_score: Optional[float] = None
    rules_matched: list[str] = []
    alert_id: Optional[uuid.UUID] = None
    explanation_id: Optional[uuid.UUID] = None
    risk_score: Optional[int] = None
    classification: Optional[str] = None
    processing_time_ms: Optional[float] = None
    status: str = "processed"
    message: Optional[str] = None


class EventResponse(BaseModel):
    """Full event response."""
    id: uuid.UUID
    timestamp: datetime
    source_ip: str
    dest_ip: str
    source_port: Optional[int]
    dest_port: Optional[int]
    protocol: str
    event_type: str
    raw_data: dict[str, Any]
    created_at: datetime

    class Config:
        from_attributes = True


class EventListResponse(BaseModel):
    """Paginated event list response."""
    events: list[EventResponse]
    total: int
    page: int
    limit: int


# =============================================================================
# Layer 2: Processed Event Schemas
# =============================================================================

class NetworkInfo(BaseModel):
    """Network information structure."""
    source: dict[str, Any]
    destination: dict[str, Any]
    protocol: str


class TemporalInfo(BaseModel):
    """Temporal information structure."""
    timestamp: datetime
    hour_of_day: int = Field(..., ge=0, le=23)
    day_of_week: int = Field(..., ge=0, le=6)
    is_business_hours: bool


class AssetInfo(BaseModel):
    """Asset information structure."""
    hostname: Optional[str] = None
    criticality: int = Field(..., ge=1, le=100)


class ParsedFields(BaseModel):
    """Normalized event structure."""
    network: NetworkInfo
    temporal: TemporalInfo
    asset: AssetInfo


class ProcessedEventResponse(BaseModel):
    """Processed event response."""
    id: uuid.UUID
    event_id: uuid.UUID
    parsed_fields: dict[str, Any]
    asset_hostname: Optional[str]
    asset_criticality: Optional[int]
    event_hash: str
    processing_timestamp: datetime
    processing_duration_ms: Optional[int]

    class Config:
        from_attributes = True


# =============================================================================
# Layer 3: Neural Detection Schemas
# =============================================================================

class NeuralDetectionResponse(BaseModel):
    """Neural detection result response."""
    id: uuid.UUID
    processed_event_id: uuid.UUID
    anomaly_score: float = Field(..., ge=0, le=1)
    frequency_score: float = Field(..., ge=0, le=1)
    port_score: float = Field(..., ge=0, le=1)
    temporal_score: float = Field(..., ge=0, le=1)
    geographic_score: float = Field(..., ge=0, le=1)
    detection_timestamp: datetime
    model_version: str

    class Config:
        from_attributes = True


# =============================================================================
# Layer 4: Rules & Evaluations Schemas
# =============================================================================

class RuleCreate(BaseModel):
    """Rule creation request."""
    rule_id: str = Field(..., max_length=50)
    name: str = Field(..., max_length=200)
    category: str = Field(..., max_length=50)
    conditions: dict[str, Any]
    severity: str = Field(..., pattern="^(LOW|MEDIUM|HIGH)$")
    enabled: bool = True


class RuleResponse(BaseModel):
    """Rule response."""
    rule_id: str
    name: str
    category: str
    conditions: dict[str, Any]
    severity: str
    enabled: bool
    created_at: datetime

    class Config:
        from_attributes = True


class RuleEvaluationResponse(BaseModel):
    """Rule evaluation result response."""
    id: uuid.UUID
    processed_event_id: uuid.UUID
    rule_id: str
    matched: bool
    severity: Optional[str]
    evaluation_timestamp: datetime

    class Config:
        from_attributes = True


# =============================================================================
# Layer 5: Alert Schemas
# =============================================================================

class AlertResponse(BaseModel):
    """Alert response."""
    id: uuid.UUID
    event_id: uuid.UUID
    processed_event_id: uuid.UUID
    neural_detection_id: Optional[uuid.UUID]
    composite_risk_score: int = Field(..., ge=0, le=100)
    classification: str
    alert_category: Optional[str]
    status: str
    assigned_to: Optional[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class AlertDetailResponse(AlertResponse):
    """Alert with full details including explanation."""
    event: Optional[EventResponse] = None
    processed_event: Optional[ProcessedEventResponse] = None
    neural_detection: Optional[NeuralDetectionResponse] = None
    explanation: Optional["ExplanationResponse"] = None
    decisions: list["DecisionResponse"] = []


class AlertListResponse(BaseModel):
    """Paginated alert list response."""
    alerts: list[AlertResponse]
    total: int
    page: int
    limit: int


# =============================================================================
# Layer 6: Explanation Schemas
# =============================================================================

class EvidenceFactor(BaseModel):
    """Evidence factor in explanation."""
    type: str
    factor: str
    weight: str
    detail: str
    score: Optional[float] = None


class RuleTriggered(BaseModel):
    """Rule triggered information."""
    rule_id: str
    name: str
    severity: str
    why_matched: str


class Counterfactual(BaseModel):
    """Counterfactual scenario."""
    question: str
    result: str


class ExplanationData(BaseModel):
    """Full explanation structure."""
    alert_id: uuid.UUID
    summary: str
    risk_assessment: dict[str, Any]
    evidence: dict[str, list[EvidenceFactor]]
    rules_triggered: list[RuleTriggered]
    historical_context: dict[str, Any]
    counterfactuals: list[Counterfactual]


class ExplanationResponse(BaseModel):
    """Explanation response."""
    id: uuid.UUID
    alert_id: uuid.UUID
    explanation_data: dict[str, Any]
    generated_at: datetime
    generation_duration_ms: Optional[int]

    class Config:
        from_attributes = True


# =============================================================================
# Layer 7: Decision Schemas
# =============================================================================

class DecisionRequest(BaseModel):
    """Decision request - analyst action on alert."""
    action: str = Field(..., pattern="^(ESCALATE|DISMISS|MARK_SAFE|WATCH)$")
    justification: str = Field(..., min_length=10, max_length=500)
    confidence: Optional[float] = Field(None, ge=0.0, le=1.0)
    follow_up_required: bool = False
    follow_up_hours: Optional[int] = Field(None, ge=1, le=720)

    @model_validator(mode="after")
    def validate_follow_up_requirements(self) -> "DecisionRequest":
        if self.follow_up_required and self.follow_up_hours is None:
            raise ValueError("follow_up_hours is required when follow_up_required is true")
        return self


class DecisionResponse(BaseModel):
    """Decision response."""
    id: uuid.UUID
    alert_id: uuid.UUID
    analyst_id: str
    action: str
    justification: str
    confidence: Optional[float]
    follow_up_required: bool
    follow_up_deadline: Optional[datetime]
    decision_timestamp: datetime
    ip_address: Optional[str]
    user_agent: Optional[str]

    class Config:
        from_attributes = True


class DecisionHistoryResponse(BaseModel):
    """Decision history for an alert."""
    alert_id: uuid.UUID
    decisions: list[DecisionResponse]
    total: int


# =============================================================================
# System Schemas
# =============================================================================

class HealthResponse(BaseModel):
    """Health check response."""
    status: str
    database: str
    redis: str
    timestamp: datetime


class MetricsResponse(BaseModel):
    """System metrics response."""
    events_processed_24h: int
    alerts_pending: int
    avg_processing_time_ms: float
    system_load: dict[str, Any]


# =============================================================================
# Audit Schemas
# =============================================================================

class AuditLogResponse(BaseModel):
    """Audit log entry response."""
    id: uuid.UUID
    entity_type: str
    entity_id: Optional[uuid.UUID]
    action: str
    user_id: Optional[uuid.UUID]
    timestamp: datetime
    details: Optional[dict[str, Any]]

    class Config:
        from_attributes = True


class AuditEntryResponse(BaseModel):
    """Standalone audit entry response model returned by audit endpoints."""
    id: uuid.UUID
    event_type: str
    actor: str
    action: str
    resource_type: Optional[str]
    resource_id: Optional[uuid.UUID]
    result: str
    metadata: Optional[dict[str, Any]]
    timestamp: datetime
    ip_address: Optional[str]

    class Config:
        from_attributes = True


class AuditListResponse(BaseModel):
    """Paginated audit log response."""
    audit_entries: list[AuditEntryResponse]
    total: int
    page: int
    limit: int


# =============================================================================
# Error Schemas
# =============================================================================

class ErrorResponse(BaseModel):
    """Standard error response."""
    detail: str
    error_code: Optional[str] = None


class ValidationErrorResponse(BaseModel):
    """Validation error response."""
    detail: list[dict[str, Any]]


# Update forward references
AlertDetailResponse.model_rebuild()

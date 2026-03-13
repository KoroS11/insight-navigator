"""
NSA-X Database Models
All tables following the exact specification
"""
import uuid
from datetime import datetime, timezone
from typing import Any, Optional

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    Numeric,
    String,
    Text,
    UniqueConstraint,
    JSON,
)
from sqlalchemy.dialects.postgresql import JSONB as PG_JSONB, UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.types import TypeDecorator, TypeEngine

from app.core.database import Base


# Custom type that uses INET for PostgreSQL and String for SQLite
class IpAddressType(TypeDecorator):
    """IP address type that works with both PostgreSQL and SQLite."""
    impl = String(45)  # Max length for IPv6
    cache_ok = True
    
    def load_dialect_impl(self, dialect: Any) -> TypeEngine:
        if dialect.name == "postgresql":
            from sqlalchemy.dialects.postgresql import INET
            return dialect.type_descriptor(INET())
        return dialect.type_descriptor(String(45))


# Custom JSONB type that falls back to JSON for SQLite
class JsonbType(TypeDecorator):
    """JSONB type that works with both PostgreSQL and SQLite."""
    impl = JSON
    cache_ok = True
    
    def load_dialect_impl(self, dialect: Any) -> TypeEngine:
        if dialect.name == "postgresql":
            return dialect.type_descriptor(PG_JSONB())
        return dialect.type_descriptor(JSON())


# Custom UUID type that works with both PostgreSQL and SQLite
class UUIDType(TypeDecorator):
    """UUID type that works with both PostgreSQL and SQLite."""
    impl = String(36)
    cache_ok = True
    
    def load_dialect_impl(self, dialect: Any) -> TypeEngine:
        if dialect.name == "postgresql":
            return dialect.type_descriptor(PG_UUID(as_uuid=True))
        return dialect.type_descriptor(String(36))
    
    def process_bind_param(self, value: Any, dialect: Any) -> Any:
        if value is None:
            return None
        if dialect.name == "postgresql":
            return value
        # For SQLite, store as string
        return str(value) if not isinstance(value, str) else value
    
    def process_result_value(self, value: Any, dialect: Any) -> Any:
        if value is None:
            return None
        if dialect.name == "postgresql":
            return value
        # For SQLite, convert back to UUID
        return uuid.UUID(value) if isinstance(value, str) else value


# Alias for UUID that works with both dialects
def UUID(as_uuid: bool = True):
    """UUID type that works with both PostgreSQL and SQLite."""
    return UUIDType() if as_uuid else String(36)


# Use our custom JSONB type
JSONB = JsonbType


def utcnow() -> datetime:
    """Get current UTC timestamp."""
    return datetime.now(timezone.utc)


# =============================================================================
# LAYER 1: Events (Raw Ingestion)
# =============================================================================

class Event(Base):
    """Raw security events - stores exactly what was received."""
    
    __tablename__ = "events"
    
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    timestamp: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        index=True,
    )
    source_ip: Mapped[str] = mapped_column(IpAddressType, nullable=False)
    dest_ip: Mapped[str] = mapped_column(IpAddressType, nullable=False)
    source_port: Mapped[Optional[int]] = mapped_column(
        Integer,
        CheckConstraint("source_port BETWEEN 0 AND 65535"),
        nullable=True,
    )
    dest_port: Mapped[Optional[int]] = mapped_column(
        Integer,
        CheckConstraint("dest_port BETWEEN 0 AND 65535"),
        nullable=True,
    )
    protocol: Mapped[str] = mapped_column(String(10), nullable=False)
    event_type: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    raw_data: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=utcnow,
        index=True,
    )
    
    # Relationships
    processed_event: Mapped[Optional["ProcessedEvent"]] = relationship(
        back_populates="event",
        uselist=False,
    )
    alerts: Mapped[list["Alert"]] = relationship(back_populates="event")


# =============================================================================
# LAYER 2: Processed Events
# =============================================================================

class ProcessedEvent(Base):
    """Normalized and enriched events."""
    
    __tablename__ = "processed_events"
    
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    event_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("events.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    parsed_fields: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False)
    asset_hostname: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    asset_criticality: Mapped[Optional[int]] = mapped_column(
        Integer,
        CheckConstraint("asset_criticality BETWEEN 1 AND 100"),
        nullable=True,
    )
    event_hash: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    processing_timestamp: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=utcnow,
    )
    processing_duration_ms: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    
    # Relationships
    event: Mapped["Event"] = relationship(back_populates="processed_event")
    neural_detection: Mapped[Optional["NeuralDetection"]] = relationship(
        back_populates="processed_event",
        uselist=False,
    )
    rule_evaluations: Mapped[list["RuleEvaluation"]] = relationship(
        back_populates="processed_event"
    )
    alerts: Mapped[list["Alert"]] = relationship(back_populates="processed_event")


# =============================================================================
# LAYER 3: Neural Detections
# =============================================================================

class NeuralDetection(Base):
    """Anomaly detection results from neural layer."""
    
    __tablename__ = "neural_detections"
    
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    processed_event_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("processed_events.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    anomaly_score: Mapped[float] = mapped_column(
        Numeric(3, 2),
        CheckConstraint("anomaly_score BETWEEN 0 AND 1"),
        nullable=False,
    )
    frequency_score: Mapped[float] = mapped_column(
        Numeric(3, 2),
        CheckConstraint("frequency_score BETWEEN 0 AND 1"),
        nullable=False,
    )
    port_score: Mapped[float] = mapped_column(
        Numeric(3, 2),
        CheckConstraint("port_score BETWEEN 0 AND 1"),
        nullable=False,
    )
    temporal_score: Mapped[float] = mapped_column(
        Numeric(3, 2),
        CheckConstraint("temporal_score BETWEEN 0 AND 1"),
        nullable=False,
    )
    geographic_score: Mapped[float] = mapped_column(
        Numeric(3, 2),
        CheckConstraint("geographic_score BETWEEN 0 AND 1"),
        nullable=False,
    )
    detection_timestamp: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=utcnow,
    )
    model_version: Mapped[str] = mapped_column(String(50), nullable=False)
    
    # Relationships
    processed_event: Mapped["ProcessedEvent"] = relationship(
        back_populates="neural_detection"
    )
    alerts: Mapped[list["Alert"]] = relationship(back_populates="neural_detection")


# =============================================================================
# LAYER 4: Rules & Rule Evaluations
# =============================================================================

class Rule(Base):
    """Security rules for symbolic reasoning."""
    
    __tablename__ = "rules"
    
    rule_id: Mapped[str] = mapped_column(String(50), primary_key=True)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    category: Mapped[str] = mapped_column(String(50), nullable=False)
    conditions: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False)
    severity: Mapped[str] = mapped_column(
        String(20),
        CheckConstraint("severity IN ('LOW', 'MEDIUM', 'HIGH')"),
        nullable=False,
    )
    enabled: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=utcnow,
    )
    
    # Relationships
    evaluations: Mapped[list["RuleEvaluation"]] = relationship(back_populates="rule")


class RuleEvaluation(Base):
    """Results of rule evaluations against events."""
    
    __tablename__ = "rule_evaluations"
    
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    processed_event_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("processed_events.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    rule_id: Mapped[str] = mapped_column(
        String(50),
        ForeignKey("rules.rule_id"),
        nullable=False,
        index=True,
    )
    matched: Mapped[bool] = mapped_column(Boolean, nullable=False)
    severity: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    evaluation_timestamp: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=utcnow,
    )
    
    # Relationships
    processed_event: Mapped["ProcessedEvent"] = relationship(
        back_populates="rule_evaluations"
    )
    rule: Mapped["Rule"] = relationship(back_populates="evaluations")


# =============================================================================
# LAYER 5: Alerts
# =============================================================================

class Alert(Base):
    """Security alerts combining neural and symbolic analysis."""
    
    __tablename__ = "alerts"
    
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    event_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("events.id"),
        nullable=False,
        index=True,
    )
    processed_event_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("processed_events.id"),
        nullable=False,
    )
    neural_detection_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("neural_detections.id"),
        nullable=True,
    )
    composite_risk_score: Mapped[int] = mapped_column(
        Integer,
        CheckConstraint("composite_risk_score BETWEEN 0 AND 100"),
        nullable=False,
    )
    classification: Mapped[str] = mapped_column(
        String(20),
        CheckConstraint("classification IN ('LOW', 'MEDIUM', 'HIGH')"),
        nullable=False,
    )
    alert_category: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    status: Mapped[str] = mapped_column(
        String(20),
        CheckConstraint("status IN ('PENDING', 'ESCALATED', 'DISMISSED', 'RESOLVED')"),
        default="PENDING",
    )
    assigned_to: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=utcnow,
        index=True,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=utcnow,
        onupdate=utcnow,
    )
    
    # Relationships
    event: Mapped["Event"] = relationship(back_populates="alerts")
    processed_event: Mapped["ProcessedEvent"] = relationship(back_populates="alerts")
    neural_detection: Mapped[Optional["NeuralDetection"]] = relationship(
        back_populates="alerts"
    )
    explanation: Mapped[Optional["Explanation"]] = relationship(
        back_populates="alert",
        uselist=False,
    )
    decisions: Mapped[list["Decision"]] = relationship(back_populates="alert")
    
    __table_args__ = (
        Index("idx_alerts_status", "status"),
        Index("idx_alerts_classification", "classification"),
    )


# =============================================================================
# LAYER 6: Explanations
# =============================================================================

class Explanation(Base):
    """Human-readable explanations for alerts."""
    
    __tablename__ = "explanations"
    
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    alert_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("alerts.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
        index=True,
    )
    explanation_data: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False)
    generated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=utcnow,
    )
    generation_duration_ms: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    
    # Relationships
    alert: Mapped["Alert"] = relationship(back_populates="explanation")


# =============================================================================
# LAYER 7: Decisions (IMMUTABLE)
# =============================================================================

class Decision(Base):
    """Analyst decisions - IMMUTABLE, never updated or deleted."""
    
    __tablename__ = "decisions"
    
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    alert_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("alerts.id"),
        nullable=False,
        index=True,
    )
    analyst_id: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    action: Mapped[str] = mapped_column(
        String(20),
        CheckConstraint("action IN ('ESCALATE', 'DISMISS', 'MARK_SAFE', 'WATCH')"),
        nullable=False,
    )
    justification: Mapped[str] = mapped_column(
        Text,
        CheckConstraint("LENGTH(justification) >= 10"),
        nullable=False,
    )
    confidence: Mapped[Optional[float]] = mapped_column(
        Numeric(3, 2),
        CheckConstraint("confidence BETWEEN 0 AND 1"),
        nullable=True,
    )
    follow_up_required: Mapped[bool] = mapped_column(Boolean, default=False)
    follow_up_deadline: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    decision_timestamp: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=utcnow,
        index=True,
    )
    ip_address: Mapped[Optional[str]] = mapped_column(IpAddressType, nullable=True)
    user_agent: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    
    # Relationships
    alert: Mapped["Alert"] = relationship(back_populates="decisions")


# =============================================================================
# Audit Log
# =============================================================================

class AuditLog(Base):
    """Immutable audit log for all system actions."""
    
    __tablename__ = "audit_log"
    
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    event_type: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    actor: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    action: Mapped[str] = mapped_column(String(200), nullable=False)
    resource_type: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    resource_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        nullable=True,
    )
    result: Mapped[str] = mapped_column(
        String(20),
        CheckConstraint("result IN ('SUCCESS', 'FAILURE')"),
        nullable=False,
    )
    extra_data: Mapped[Optional[dict[str, Any]]] = mapped_column(JSONB, nullable=True)
    timestamp: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=utcnow,
        index=True,
    )
    ip_address: Mapped[Optional[str]] = mapped_column(IpAddressType, nullable=True)


# =============================================================================
# Users (for authentication)
# =============================================================================

class User(Base):
    """System users for authentication."""
    
    __tablename__ = "users"
    
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    username: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    full_name: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    role: Mapped[str] = mapped_column(String(50), default="analyst")
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=utcnow,
    )
    last_login: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

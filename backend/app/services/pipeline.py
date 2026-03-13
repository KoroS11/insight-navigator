"""
NSA-X Pipeline Orchestrator
Coordinates the full 7-layer processing pipeline.
"""
import time
import uuid
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import (
    Alert,
    AuditLog,
    Decision,
    Event,
    Explanation,
    NeuralDetection,
    ProcessedEvent,
    RuleEvaluation,
)
from app.services.layer1_ingestion import IngestionService
from app.services.layer2_processing import ProcessingService
from app.services.layer3_neural import NeuralDetectionService
from app.services.layer4_symbolic import SymbolicReasoningService
from app.services.layer5_integration import IntegrationService
from app.services.layer6_explainability import ExplainabilityService
from app.services.layer7_decisions import DecisionService


@dataclass
class PipelineResult:
    """Result of full pipeline execution."""
    event: Event
    processed_event: ProcessedEvent
    detection: NeuralDetection
    evaluations: list[RuleEvaluation]
    alert: Alert | None
    explanation: Explanation | None
    processing_time_ms: float


class PipelineOrchestrator:
    """
    Orchestrates the 7-layer processing pipeline.
    
    Flow:
    Event → Layer 1 (Ingest) → Layer 2 (Process) → Layer 3 (Neural) 
         → Layer 4 (Symbolic) → Layer 5 (Integrate) → Layer 6 (Explain)
    
    Layer 7 (Decision) is invoked separately by analyst action.
    """
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self.ingestion = IngestionService(db)
        self.processing = ProcessingService(db)
        self.neural = NeuralDetectionService(db)
        self.symbolic = SymbolicReasoningService(db)
        self.integration = IntegrationService(db)
        self.explainability = ExplainabilityService(db)
        self.decisions = DecisionService(db)
    
    async def process_event(
        self,
        event_type: str,
        source_ip: str,
        dest_ip: str,
        dest_port: int | None = None,
        protocol: str | None = None,
        timestamp: datetime | None = None,
        raw_data: dict[str, Any] | None = None,
    ) -> PipelineResult:
        """
        Process an event through the full pipeline (Layers 1-6).
        
        Performance requirement: <2s total latency
        """
        start_time = time.time()
        
        try:
            # Layer 1: Ingestion
            event = await self.ingestion.ingest_event(
                event_type=event_type,
                source_ip=source_ip,
                dest_ip=dest_ip,
                dest_port=dest_port,
                protocol=protocol or "TCP",
                timestamp=timestamp or datetime.now(timezone.utc),
                raw_data=raw_data or {},
            )
            
            # Layer 2: Processing
            processed_event = await self.processing.process_event(event)
            
            # Layer 3: Neural Detection
            detection = await self.neural.detect_anomalies(processed_event)
            
            # Get event count for frequency-based rules
            event_count = await self._get_event_count_24h(event.source_ip)
            
            # Layer 4: Symbolic Reasoning
            await self.symbolic.ensure_default_rules()
            evaluations = await self.symbolic.evaluate_rules(
                processed_event=processed_event,
                event_count_24h=event_count,
            )
            
            # Layer 5: Integration
            alert = await self.integration.integrate_reasoning(
                processed_event=processed_event,
                detection=detection,
                evaluations=evaluations,
            )
            
            # Layer 6: Explainability (only if alert created)
            explanation = None
            if alert:
                explanation = await self.explainability.generate_explanation(
                    alert=alert,
                    detection=detection,
                    evaluations=evaluations,
                    processed_event=processed_event,
                    event=event,
                )
            
            # Commit all changes
            await self.db.commit()
            
            processing_time = (time.time() - start_time) * 1000
            
            return PipelineResult(
                event=event,
                processed_event=processed_event,
                detection=detection,
                evaluations=evaluations,
                alert=alert,
                explanation=explanation,
                processing_time_ms=round(processing_time, 2),
            )
        except Exception:
            await self.db.rollback()
            raise
    
    async def record_analyst_decision(
        self,
        alert_id: uuid.UUID,
        analyst_id: uuid.UUID,
        decision_type: str,
        rationale: str,
        confidence: float | None = None,
    ) -> Decision:
        """
        Record an analyst decision (Layer 7).
        This is invoked separately from the main pipeline.
        """
        try:
            decision = await self.decisions.record_decision(
                alert_id=alert_id,
                analyst_id=analyst_id,
                decision_type=decision_type,
                rationale=rationale,
                confidence=confidence,
            )
            await self.db.commit()
            return decision
        except Exception:
            await self.db.rollback()
            raise
    
    async def _get_event_count_24h(self, source_ip: str) -> int:
        """Get count of events from source IP in last 24 hours."""
        from datetime import timedelta
        
        cutoff = datetime.now(timezone.utc) - timedelta(hours=24)
        result = await self.db.execute(
            select(func.count(Event.id))
            .where(Event.source_ip == source_ip)
            .where(Event.created_at >= cutoff)
        )
        return result.scalar() or 0
    
    async def get_alert_full_context(self, alert_id: uuid.UUID) -> dict[str, Any] | None:
        """Get full context for an alert including all related data."""
        # Get alert
        alert = await self.integration.get_alert(alert_id)
        if not alert:
            return None
        
        # Get processed event
        processed_result = await self.db.execute(
            select(ProcessedEvent).where(ProcessedEvent.id == alert.processed_event_id)
        )
        processed_event = processed_result.scalar_one_or_none()
        
        # Get original event
        event = None
        if processed_event:
            event_result = await self.db.execute(
                select(Event).where(Event.id == processed_event.event_id)
            )
            event = event_result.scalar_one_or_none()
        
        # Get detection
        detection = None
        if alert.neural_detection_id:
            detection_result = await self.db.execute(
                select(NeuralDetection).where(NeuralDetection.id == alert.neural_detection_id)
            )
            detection = detection_result.scalar_one_or_none()
        
        # Get evaluations
        evaluations = []
        if processed_event:
            evaluations = await self.symbolic.get_evaluations(processed_event.id)
        
        # Get explanation
        explanation = await self.explainability.get_explanation(alert_id)
        
        # Get decisions
        decisions = await self.decisions.get_decisions_for_alert(alert_id)
        
        return {
            "alert": alert,
            "event": event,
            "processed_event": processed_event,
            "detection": detection,
            "evaluations": evaluations,
            "explanation": explanation,
            "decisions": decisions,
        }
    
    async def get_system_health(self) -> dict[str, Any]:
        """Get system health metrics."""
        # Count totals
        event_count = (await self.db.execute(select(func.count(Event.id)))).scalar() or 0
        alert_count = (await self.db.execute(select(func.count(Alert.id)))).scalar() or 0
        
        open_alerts = (await self.db.execute(
            select(func.count(Alert.id)).where(Alert.status == "open")
        )).scalar() or 0
        
        decision_count = (await self.db.execute(select(func.count(Decision.id)))).scalar() or 0
        
        return {
            "status": "healthy",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "metrics": {
                "total_events": event_count,
                "total_alerts": alert_count,
                "open_alerts": open_alerts,
                "total_decisions": decision_count,
            },
        }

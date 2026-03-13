"""
NSA-X Layer 5: Reasoning Integration Service
Combines neural and symbolic reasoning to produce unified alerts.
"""
import uuid
from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Alert, NeuralDetection, ProcessedEvent, RuleEvaluation


class IntegrationService:
    """Layer 5: Combines neural detection and symbolic reasoning."""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def integrate_reasoning(
        self,
        processed_event: ProcessedEvent,
        detection: NeuralDetection,
        evaluations: list[RuleEvaluation],
    ) -> Alert | None:
        """
        Combine neural and symbolic reasoning to create alerts.
        
        Critical Rules:
        - Must consider BOTH neural scores AND rule matches
        - Alert if: anomaly_score > 0.7 OR any HIGH severity rule matches
        - Risk score formula: (neural * 60) + (max_severity_weight * 40)
        - All scores 0-100 range for final risk_score
        - Must complete in <50ms
        """
        # Check if alert should be created
        should_alert, risk_score, reasons = self._calculate_alert_decision(
            detection=detection,
            evaluations=evaluations,
        )
        
        if not should_alert:
            return None
        
        # Get highest severity from matched rules
        classification = self._get_highest_severity(evaluations)
        
        alert = Alert(
            id=uuid.uuid4(),
            event_id=processed_event.event_id,  # Link to original event
            processed_event_id=processed_event.id,
            neural_detection_id=detection.id,
            composite_risk_score=risk_score,
            classification=classification,
            status="PENDING",
            created_at=datetime.now(timezone.utc),
        )
        
        self.db.add(alert)
        await self.db.flush()
        
        return alert
    
    def _calculate_alert_decision(
        self,
        detection: NeuralDetection,
        evaluations: list[RuleEvaluation],
    ) -> tuple[bool, int, list[str]]:
        """
        Determine if an alert should be created and calculate risk score.
        
        Returns: (should_alert, risk_score, reasons)
        """
        reasons = []
        
        # Check neural detection threshold
        neural_threshold_exceeded = detection.anomaly_score >= 0.7
        if neural_threshold_exceeded:
            reasons.append(f"Anomaly score {detection.anomaly_score:.2f} exceeds threshold 0.7")
        
        # Check for matched rules
        matched_evaluations = [e for e in evaluations if e.matched]
        high_severity_match = any(e.severity == "HIGH" for e in matched_evaluations)
        
        if high_severity_match:
            reasons.append("HIGH severity rule violation detected")
        
        for eval in matched_evaluations:
            reasons.append(f"Rule {eval.rule_id} matched (severity: {eval.severity})")
        
        # Decision logic
        should_alert = neural_threshold_exceeded or high_severity_match
        
        medium_or_higher_matches = [
            evaluation for evaluation in matched_evaluations
            if evaluation.severity in {"MEDIUM", "HIGH"}
        ]

        if not should_alert and len(medium_or_higher_matches) >= 2:
            # Multiple MEDIUM/HIGH symbolic violations trigger alert.
            should_alert = True
            reasons.append("Multiple rule violations detected")
        
        # Calculate risk score
        risk_score = self._calculate_risk_score(detection, matched_evaluations)
        
        return should_alert, risk_score, reasons
    
    def _calculate_risk_score(
        self,
        detection: NeuralDetection,
        matched_evaluations: list[RuleEvaluation],
    ) -> int:
        """
        Calculate final risk score (0-100).
        
        Formula: (neural_score * 60) + (severity_weight * 40)
        """
        # Neural component (0-60 points)
        neural_component = detection.anomaly_score * 60
        
        # Severity component (0-40 points)
        severity_weights = {
            "HIGH": 1.0,
            "MEDIUM": 0.6,
            "LOW": 0.3,
        }
        
        if matched_evaluations:
            max_weight = max(
                severity_weights.get(e.severity, 0.0)
                for e in matched_evaluations
            )
        else:
            max_weight = 0.0
        
        severity_component = max_weight * 40
        
        risk_score = int(neural_component + severity_component)
        
        # Clamp to 0-100
        return max(0, min(100, risk_score))
    
    def _get_highest_severity(self, evaluations: list[RuleEvaluation]) -> str:
        """Get the highest severity from matched evaluations."""
        severity_order = {"HIGH": 3, "MEDIUM": 2, "LOW": 1}
        
        matched = [e for e in evaluations if e.matched]
        if not matched:
            return "LOW"
        
        highest = max(matched, key=lambda e: severity_order.get(e.severity, 0))
        return highest.severity or "LOW"
    
    async def get_alert(self, alert_id: uuid.UUID) -> Alert | None:
        """Get an alert by ID."""
        result = await self.db.execute(
            select(Alert).where(Alert.id == alert_id)
        )
        return result.scalar_one_or_none()
    
    async def get_alert_by_event(self, processed_event_id: uuid.UUID) -> Alert | None:
        """Get alert for a processed event."""
        result = await self.db.execute(
            select(Alert).where(Alert.processed_event_id == processed_event_id)
        )
        return result.scalar_one_or_none()
    
    async def list_alerts(
        self,
        status: str | None = None,
        classification: str | None = None,
        limit: int = 100,
        offset: int = 0,
    ) -> list[Alert]:
        """List alerts with optional filtering."""
        query = select(Alert)
        
        if status:
            query = query.where(Alert.status == status)
        if classification:
            query = query.where(Alert.classification == classification)
        
        query = query.order_by(Alert.created_at.desc()).offset(offset).limit(limit)
        
        result = await self.db.execute(query)
        return list(result.scalars().all())
    
    async def update_alert_status(
        self,
        alert_id: uuid.UUID,
        new_status: str,
        updated_by_id: uuid.UUID | None = None,
    ) -> Alert | None:
        """Update alert status atomically.
        
        Args:
            alert_id: The alert to update
            new_status: New status value
            updated_by_id: Optional user ID who made the change (for audit)
        """
        alert = await self.get_alert(alert_id)
        if alert is None:
            return None
        
        valid_statuses = {"PENDING", "ESCALATED", "DISMISSED", "RESOLVED"}
        if new_status not in valid_statuses:
            raise ValueError(f"Invalid status: {new_status}")
        
        alert.status = new_status
        
        # Set updated_by_id atomically in same transaction if provided and supported
        if updated_by_id is not None and hasattr(alert, 'updated_by_id'):
            alert.updated_by_id = updated_by_id
        
        await self.db.flush()
        return alert

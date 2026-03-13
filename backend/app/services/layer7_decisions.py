"""
NSA-X Layer 7: Analyst Decision Service
Records immutable analyst decisions and audit trail.
"""
import uuid
from datetime import datetime, timezone
from typing import Literal

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Alert, AuditLog, Decision, User


class DecisionService:
    """Layer 7: Records immutable analyst decisions."""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def record_decision(
        self,
        alert_id: uuid.UUID,
        analyst_id: uuid.UUID,
        decision_type: Literal["accept", "reject", "escalate", "defer"],
        rationale: str,
        confidence: float | None = None,
    ) -> Decision:
        """
        Record an immutable analyst decision.
        
        Critical Rules:
        - NO UPDATES to existing decisions (immutable)
        - NO DELETES ever
        - Decision must be linked to valid alert
        - Confidence must be 0.0-1.0 if provided
        - Audit log entry is REQUIRED
        """
        # Validate alert exists
        alert = await self._get_alert(alert_id)
        if alert is None:
            raise ValueError(f"Alert {alert_id} not found")
        
        # Validate analyst exists
        analyst = await self._get_user(analyst_id)
        if analyst is None:
            raise ValueError(f"Analyst {analyst_id} not found")
        
        # Validate confidence range
        if confidence is not None:
            if not 0.0 <= confidence <= 1.0:
                raise ValueError("Confidence must be between 0.0 and 1.0")
        
        # Validate decision type - map to model's action values
        action_map = {
            "accept": "DISMISS",
            "reject": "MARK_SAFE",
            "escalate": "ESCALATE",
            "defer": "WATCH",
        }
        if decision_type not in action_map:
            raise ValueError(f"Invalid decision type: {decision_type}")
        
        model_action = action_map[decision_type]
        
        # Create immutable decision record
        decision = Decision(
            id=uuid.uuid4(),
            alert_id=alert_id,
            analyst_id=str(analyst_id),
            action=model_action,
            justification=rationale,
            confidence=confidence,
            decision_timestamp=datetime.now(timezone.utc),
        )
        
        self.db.add(decision)
        
        # Update alert status based on decision
        await self._update_alert_from_decision(alert, decision_type)
        
        # Create audit log entry
        await self._create_audit_log(
            entity_type="decision",
            entity_id=decision.id,
            action="create",
            user_id=analyst_id,
            details={
                "alert_id": str(alert_id),
                "decision_type": decision_type,
                "rationale_length": len(rationale),
            },
        )
        
        await self.db.flush()
        
        return decision
    
    async def _get_alert(self, alert_id: uuid.UUID) -> Alert | None:
        """Get alert by ID."""
        result = await self.db.execute(
            select(Alert).where(Alert.id == alert_id)
        )
        return result.scalar_one_or_none()
    
    async def _get_user(self, user_id: uuid.UUID) -> User | None:
        """Get user by ID."""
        result = await self.db.execute(
            select(User).where(User.id == user_id)
        )
        return result.scalar_one_or_none()
    
    async def _update_alert_from_decision(
        self,
        alert: Alert,
        decision_type: str,
    ) -> None:
        """Update alert status based on decision type."""
        status_mapping = {
            "accept": "RESOLVED",
            "reject": "DISMISSED",
            "escalate": "ESCALATED",
            "defer": "PENDING",
        }
        
        new_status = status_mapping.get(decision_type)
        if new_status:
            alert.status = new_status
    
    async def _create_audit_log(
        self,
        entity_type: str,
        entity_id: uuid.UUID,
        action: str,
        user_id: uuid.UUID,
        details: dict,
    ) -> AuditLog:
        """Create an audit log entry."""
        audit = AuditLog(
            id=uuid.uuid4(),
            event_type=entity_type.upper(),
            actor=str(user_id),
            action=action,
            resource_type=entity_type,
            resource_id=entity_id,
            result="SUCCESS",
            extra_data=details,
            timestamp=datetime.now(timezone.utc),
        )
        self.db.add(audit)
        return audit
    
    async def get_decision(self, decision_id: uuid.UUID) -> Decision | None:
        """Get a decision by ID (read-only)."""
        result = await self.db.execute(
            select(Decision).where(Decision.id == decision_id)
        )
        return result.scalar_one_or_none()
    
    async def get_decisions_for_alert(self, alert_id: uuid.UUID) -> list[Decision]:
        """Get all decisions for an alert (may be multiple if escalated)."""
        result = await self.db.execute(
            select(Decision)
            .where(Decision.alert_id == alert_id)
            .order_by(Decision.decision_timestamp)
        )
        return list(result.scalars().all())
    
    async def get_decision_by_alert(self, alert_id: uuid.UUID) -> Decision | None:
        """Get the most recent decision for an alert."""
        result = await self.db.execute(
            select(Decision)
            .where(Decision.alert_id == alert_id)
            .order_by(Decision.decision_timestamp.desc())
            .limit(1)
        )
        return result.scalar_one_or_none()
    
    async def get_decisions_by_analyst(
        self,
        analyst_id: uuid.UUID,
        limit: int = 100,
        offset: int = 0,
    ) -> list[Decision]:
        """Get decisions made by a specific analyst."""
        limit, offset = self._validate_pagination(limit=limit, offset=offset)

        result = await self.db.execute(
            select(Decision)
            .where(Decision.analyst_id == str(analyst_id))
            .order_by(Decision.decision_timestamp.desc())
            .offset(offset)
            .limit(limit)
        )
        return list(result.scalars().all())
    
    async def list_decisions_by_analyst(
        self,
        analyst_id: uuid.UUID,
        limit: int = 100,
        offset: int = 0,
    ) -> list[Decision]:
        """Alias for get_decisions_by_analyst."""
        return await self.get_decisions_by_analyst(analyst_id, limit, offset)
    
    async def get_audit_trail(
        self,
        entity_type: str | None = None,
        entity_id: uuid.UUID | None = None,
        user_id: uuid.UUID | None = None,
        limit: int = 100,
        offset: int = 0,
    ) -> list[AuditLog]:
        """Query audit trail with optional filters."""
        limit, offset = self._validate_pagination(limit=limit, offset=offset)

        query = select(AuditLog)
        
        if entity_type:
            query = query.where(AuditLog.event_type == entity_type.upper())
        if entity_id:
            query = query.where(AuditLog.resource_id == entity_id)
        if user_id:
            query = query.where(AuditLog.actor == str(user_id))
        
        query = query.order_by(AuditLog.timestamp.desc()).offset(offset).limit(limit)
        
        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def create_decision(
        self,
        alert_id: uuid.UUID,
        analyst_id: uuid.UUID,
        action: str,
        reasoning: str,
        confidence: float | None = None,
    ) -> Decision:
        """
        Create an immutable analyst decision.
        Alias for record_decision with action/reasoning terminology.
        """
        # Map action to decision_type
        action_map = {
            "approve": "accept",
            "accept": "accept",
            "reject": "reject",
            "escalate": "escalate",
            "defer": "defer",
        }
        
        if action not in action_map:
            raise ValueError(f"Invalid action: {action}")
        
        decision_type = action_map[action]
        
        return await self.record_decision(
            alert_id=alert_id,
            analyst_id=analyst_id,
            decision_type=decision_type,
            rationale=reasoning,
            confidence=confidence,
        )

    async def list_decisions(
        self,
        analyst_id: uuid.UUID | None = None,
        limit: int = 100,
        offset: int = 0,
    ) -> list[Decision]:
        """List decisions, optionally filtered by analyst."""
        limit, offset = self._validate_pagination(limit=limit, offset=offset)

        if analyst_id:
            return await self.get_decisions_by_analyst(analyst_id, limit, offset)
        
        result = await self.db.execute(
            select(Decision)
            .order_by(Decision.decision_timestamp.desc())
            .offset(offset)
            .limit(limit)
        )
        return list(result.scalars().all())
    
    async def get_statistics(self, analyst_id: uuid.UUID | None = None) -> dict:
        """Get decision statistics, optionally filtered by analyst."""
        from sqlalchemy import func
        
        query = select(
            func.count(Decision.id).label("total"),
            func.count(Decision.id).filter(Decision.action == "ESCALATE").label("escalated"),
            func.count(Decision.id).filter(Decision.action == "DISMISS").label("dismissed"),
            func.count(Decision.id).filter(Decision.action == "MARK_SAFE").label("marked_safe"),
            func.count(Decision.id).filter(Decision.action == "WATCH").label("watch"),
        )
        
        if analyst_id:
            query = query.where(Decision.analyst_id == str(analyst_id))
        
        result = await self.db.execute(query)
        row = result.one()
        
        return {
            "total": row.total or 0,
            "escalated": row.escalated or 0,
            "dismissed": row.dismissed or 0,
            "marked_safe": row.marked_safe or 0,
            "watch": row.watch or 0,
        }

    def _validate_pagination(self, limit: int, offset: int) -> tuple[int, int]:
        """Validate pagination values used by list/query operations."""
        try:
            limit = int(limit)
            offset = int(offset)
        except (TypeError, ValueError) as exc:
            raise ValueError("limit and offset must be integers") from exc

        if limit <= 0:
            raise ValueError("limit must be greater than 0")
        if offset < 0:
            raise ValueError("offset must be greater than or equal to 0")
        return limit, offset

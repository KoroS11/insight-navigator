"""
NSA-X Alerts Router
Handles alert management and analyst decisions.
"""
import uuid
from typing import Annotated, Literal

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from app.core import get_db, security
from app.models import User
from app.schemas import (
    AlertDetailResponse,
    AlertResponse,
    DecisionRequest,
    DecisionResponse,
    ExplanationResponse,
)
from app.services import PipelineOrchestrator

router = APIRouter(prefix="/alerts", tags=["alerts"])


@router.get("/", response_model=list[AlertResponse])
async def list_alerts(
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(security.get_current_user)],
    status_filter: str | None = Query(default=None, alias="status"),
    classification: str | None = None,
    limit: int = Query(default=100, ge=1, le=1000),
    offset: int = Query(default=0, ge=0),
):
    """List alerts with optional filtering."""
    from app.services import IntegrationService
    
    service = IntegrationService(db)
    alerts = await service.list_alerts(
        status=status_filter,
        classification=classification,
        limit=limit,
        offset=offset,
    )
    
    return [AlertResponse.model_validate(a) for a in alerts]


@router.get("/{alert_id}", response_model=AlertDetailResponse)
async def get_alert(
    alert_id: uuid.UUID,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(security.get_current_user)],
):
    """Get full alert context including explanation and decisions."""
    pipeline = PipelineOrchestrator(db)
    context = await pipeline.get_alert_full_context(alert_id)
    
    if not context:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Alert {alert_id} not found",
        )
    
    # Defensively check for alert key
    alert = context.get("alert")
    if alert is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Alert {alert_id} not found",
        )
    
    return AlertDetailResponse(
        id=alert.id,
        event_id=alert.event_id,
        processed_event_id=alert.processed_event_id,
        neural_detection_id=alert.neural_detection_id,
        composite_risk_score=alert.composite_risk_score,
        classification=alert.classification,
        alert_category=alert.alert_category,
        status=alert.status,
        assigned_to=alert.assigned_to,
        created_at=alert.created_at,
        updated_at=alert.updated_at,
        explanation=ExplanationResponse.model_validate(context["explanation"]) if context.get("explanation") else None,
        decisions=[DecisionResponse.model_validate(d) for d in context.get("decisions", [])],
    )


class StatusUpdate(BaseModel):
    """Alert status update request."""
    status: Literal["PENDING", "ESCALATED", "DISMISSED", "RESOLVED"]


@router.patch("/{alert_id}/status", response_model=AlertResponse)
async def update_alert_status(
    alert_id: uuid.UUID,
    update: StatusUpdate,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(security.get_current_user)],
):
    """Update alert status."""
    from app.services import IntegrationService
    
    service = IntegrationService(db)
    
    try:
        # Pass user ID for atomic update (status + updated_by_id in one transaction)
        alert = await service.update_alert_status(
            alert_id=alert_id,
            new_status=update.status,
            updated_by_id=current_user.id,
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    
    if not alert:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Alert {alert_id} not found",
        )
    
    return AlertResponse.model_validate(alert)


@router.post("/{alert_id}/decisions", response_model=DecisionResponse, status_code=status.HTTP_201_CREATED)
async def create_decision(
    alert_id: uuid.UUID,
    decision_data: DecisionRequest,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(security.get_current_user)],
):
    """
    Record an analyst decision for an alert.
    
    This is Layer 7 of the NSA-X pipeline.
    Decisions are IMMUTABLE - they cannot be updated or deleted.
    """
    pipeline = PipelineOrchestrator(db)
    
    # Map schema action to decision_type (service expects accept/reject/escalate/defer)
    # Semantics:
    # - DISMISS: Accept the alert (threat was real, now handled) -> RESOLVED
    # - MARK_SAFE: Reject the alert (false positive) -> DISMISSED
    # - ESCALATE: Needs higher attention -> ESCALATED
    # - WATCH: Defer for monitoring -> PENDING
    action_map = {
        "ESCALATE": "escalate",
        "DISMISS": "accept",
        "MARK_SAFE": "reject",
        "WATCH": "defer",
    }
    
    # Validate action is in the allowed set
    if decision_data.action not in action_map:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid action '{decision_data.action}'. Must be one of: {', '.join(action_map.keys())}",
        )
    
    decision_type = action_map[decision_data.action]
    
    try:
        decision = await pipeline.record_analyst_decision(
            alert_id=alert_id,
            analyst_id=current_user.id,
            decision_type=decision_type,
            rationale=decision_data.justification,
            confidence=decision_data.confidence,
        )
    except ValueError as e:
        error_msg = str(e).lower()
        # Map not-found errors to 404
        if "not found" in error_msg:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=str(e),
            )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    except (KeyError, LookupError) as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Alert {alert_id} not found",
        )
    
    if decision is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Alert {alert_id} not found",
        )
    
    return DecisionResponse.model_validate(decision)


@router.get("/{alert_id}/explanation", response_model=ExplanationResponse)
async def get_alert_explanation(
    alert_id: uuid.UUID,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(security.get_current_user)],
):
    """Get the explanation for an alert."""
    from app.services import ExplainabilityService
    
    service = ExplainabilityService(db)
    explanation = await service.get_explanation(alert_id)
    
    if not explanation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Explanation for alert {alert_id} not found",
        )
    
    return ExplanationResponse.model_validate(explanation)

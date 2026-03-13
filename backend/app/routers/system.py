"""
NSA-X System Router
Handles health checks, metrics, and system configuration.
"""
import logging
from datetime import datetime, timezone
from typing import Annotated

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.core import get_db, security
from app.models import User
from app.schemas import RuleResponse
from app.services import PipelineOrchestrator, SymbolicReasoningService

router = APIRouter(prefix="/system", tags=["system"])
logger = logging.getLogger(__name__)


class HealthResponse(BaseModel):
    """Health check response."""
    status: str
    timestamp: str
    metrics: dict


@router.get("/health", response_model=HealthResponse)
async def health_check(
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """
    System health check endpoint.
    Public endpoint - no authentication required.
    """
    pipeline = PipelineOrchestrator(db)
    health = await pipeline.get_system_health()

    if not isinstance(health, dict):
        logger.warning("PipelineOrchestrator.get_system_health() returned non-dict: %r", type(health))
        health = {}

    status_value = health.get("status", "degraded")
    timestamp_value = health.get("timestamp", datetime.now(timezone.utc).isoformat())
    metrics_value = health.get("metrics", {})
    if not isinstance(metrics_value, dict):
        logger.warning("Invalid health metrics payload type: %r", type(metrics_value))
        metrics_value = {}
    
    return HealthResponse(
        status=status_value,
        timestamp=timestamp_value,
        metrics=metrics_value,
    )


@router.get("/rules", response_model=list[RuleResponse])
async def list_rules(
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(security.get_current_user)],
    enabled_only: bool = True,
):
    """List all security rules."""
    service = SymbolicReasoningService(db)
    
    # Note: Default rules are initialized at app startup via lifespan handler
    # No need to call ensure_default_rules() on every request
    
    rules = await service.list_rules(enabled_only=enabled_only)
    
    return [
        RuleResponse(
            rule_id=r.rule_id,
            name=r.name,
            category=r.category,
            conditions=r.conditions,
            severity=r.severity,
            enabled=r.enabled,
            created_at=r.created_at,
        )
        for r in rules
    ]


@router.get("/rules/{rule_id}", response_model=RuleResponse)
async def get_rule(
    rule_id: str,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(security.get_current_user)],
):
    """Get a specific rule by ID."""
    from fastapi import HTTPException, status
    
    service = SymbolicReasoningService(db)
    rule = await service.get_rule(rule_id)
    
    if not rule:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Rule {rule_id} not found",
        )
    
    return RuleResponse(
        rule_id=rule.rule_id,
        name=rule.name,
        category=rule.category,
        conditions=rule.conditions,
        severity=rule.severity,
        enabled=rule.enabled,
        created_at=rule.created_at,
    )

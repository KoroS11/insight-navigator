"""
NSA-X Audit Router
Handles audit trail queries.
"""
import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core import get_db, security
from app.models import User
from app.schemas import AuditEntryResponse
from app.services import DecisionService

router = APIRouter(prefix="/audit", tags=["audit"])


@router.get("/", response_model=list[AuditEntryResponse])
async def get_audit_trail(
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(security.get_current_user)],
    entity_type: str | None = None,
    entity_id: uuid.UUID | None = None,
    user_id: uuid.UUID | None = None,
    limit: int = Query(default=100, ge=1, le=1000),
    offset: int = Query(default=0, ge=0),
):
    """
    Query audit trail with optional filters.
    
    Authorization:
    - Admin users can query all audit entries
    - Non-admin users can only query their own entries (user_id forced to their ID)
    """
    # Authorization check
    is_admin = current_user.role == "admin"
    
    if not is_admin:
        # Non-admins can only see their own audit entries
        if entity_type is not None or entity_id is not None:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied: Non-admin users cannot filter by entity_type or entity_id",
            )
        # Force user_id to current user
        user_id = current_user.id
    
    service = DecisionService(db)
    logs = await service.get_audit_trail(
        entity_type=entity_type,
        entity_id=entity_id,
        user_id=user_id,
        limit=limit,
        offset=offset,
    )
    
    return [
        AuditEntryResponse(
            id=log.id,
            event_type=log.event_type,
            actor=log.actor,
            action=log.action,
            resource_type=log.resource_type,
            resource_id=log.resource_id,
            result=log.result,
            metadata=log.extra_data,
            timestamp=log.timestamp,
            ip_address=log.ip_address,
        )
        for log in logs
    ]

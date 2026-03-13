"""
NSA-X Events Router
Handles event ingestion and querying.
"""
import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core import get_db, security
from app.models import User
from app.schemas import (
    EventCreate,
    EventResponse,
    PipelineResultResponse,
    ProcessedEventResponse,
)
from app.services import PipelineOrchestrator

router = APIRouter(prefix="/events", tags=["events"])


@router.post("/", response_model=PipelineResultResponse, status_code=status.HTTP_201_CREATED)
async def ingest_event(
    event_data: EventCreate,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(security.get_current_user)],
):
    """
    Ingest a new security event and process through the full pipeline.
    
    This endpoint triggers Layers 1-6 of the NSA-X pipeline:
    1. Ingestion: Store raw event
    2. Processing: Normalize and enrich
    3. Neural Detection: Anomaly scoring
    4. Symbolic Reasoning: Rule evaluation
    5. Integration: Alert generation
    6. Explainability: Explanation generation
    """
    pipeline = PipelineOrchestrator(db)
    
    result = await pipeline.process_event(
        event_type=event_data.event_type,
        source_ip=event_data.source_ip,
        dest_ip=event_data.dest_ip,
        dest_port=event_data.dest_port,
        protocol=event_data.protocol,
        timestamp=event_data.timestamp,
        raw_data=event_data.raw_data,
    )
    
    return PipelineResultResponse(
        event_id=result.event.id,
        processed_event_id=result.processed_event.id,
        anomaly_score=result.detection.anomaly_score,
        rules_matched=[e.rule_id for e in result.evaluations if e.matched],
        alert_id=result.alert.id if result.alert else None,
        risk_score=result.alert.composite_risk_score if result.alert else None,
        processing_time_ms=result.processing_time_ms,
    )


@router.get("/", response_model=list[EventResponse])
async def list_events(
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(security.get_current_user)],
    response: Response,
    event_type: str | None = None,
    limit: int = Query(default=100, ge=1, le=1000),
    offset: int = Query(default=0, ge=0),
):
    """List ingested events with optional filtering."""
    from app.services import IngestionService
    
    service = IngestionService(db)
    events, total = await service.list_events(
        event_type=event_type,
        limit=limit,
        offset=offset,
    )
    response.headers["X-Total-Count"] = str(total)
    
    return [
        EventResponse(
            id=e.id,
            timestamp=e.timestamp,
            event_type=e.event_type,
            source_ip=str(e.source_ip),
            dest_ip=str(e.dest_ip),
            source_port=e.source_port,
            dest_port=e.dest_port,
            protocol=e.protocol,
            raw_data=e.raw_data,
            created_at=e.created_at,
        )
        for e in events
    ]


@router.get("/{event_id}", response_model=EventResponse)
async def get_event(
    event_id: uuid.UUID,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(security.get_current_user)],
):
    """Get a specific event by ID."""
    from app.services import IngestionService
    
    service = IngestionService(db)
    event = await service.get_event(event_id)
    
    if not event:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Event {event_id} not found",
        )
    
    return EventResponse(
        id=event.id,
        timestamp=event.timestamp,
        event_type=event.event_type,
        source_ip=str(event.source_ip),
        dest_ip=str(event.dest_ip),
        source_port=event.source_port,
        dest_port=event.dest_port,
        protocol=event.protocol,
        raw_data=event.raw_data,
        created_at=event.created_at,
    )


@router.get("/{event_id}/processed", response_model=ProcessedEventResponse)
async def get_processed_event(
    event_id: uuid.UUID,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(security.get_current_user)],
):
    """Get processed event data for a raw event."""
    from sqlalchemy import select
    from app.models import ProcessedEvent
    
    result = await db.execute(
        select(ProcessedEvent).where(ProcessedEvent.event_id == event_id)
    )
    processed = result.scalar_one_or_none()
    
    if not processed:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Processed event for {event_id} not found",
        )
    
    return ProcessedEventResponse(
        id=processed.id,
        event_id=processed.event_id,
        parsed_fields=processed.parsed_fields,
        asset_hostname=processed.asset_hostname,
        asset_criticality=processed.asset_criticality,
        event_hash=processed.event_hash,
        processing_timestamp=processed.processing_timestamp,
        processing_duration_ms=processed.processing_duration_ms,
    )

"""
NSA-X Layer 1: Data Ingestion Service
Accepts and stores raw security events - NO analysis performed here.
"""
import uuid
from datetime import datetime, timezone
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Event
from app.schemas import EventIngestRequest, EventIngestResponse, EventResponse


class IngestionService:
    """Layer 1: Raw event ingestion - stores exactly what is received."""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def ingest_event(
        self,
        request: EventIngestRequest | None = None,
        *,
        event_type: str | None = None,
        source_ip: str | None = None,
        dest_ip: str | None = None,
        source_port: int | None = None,
        dest_port: int | None = None,
        protocol: str | None = None,
        timestamp: datetime | None = None,
        raw_data: dict[str, Any] | str | None = None,
        payload: dict[str, Any] | None = None,  # Alias for raw_data
    ) -> Event:
        """
        Ingest a raw security event.
        
        Can be called with either a request object or keyword arguments.
        
        Critical Rules:
        - Store exactly what was received
        - Generate unique event_id
        - No filtering, no rejection (except invalid format)
        - No async processing here (synchronous store)
        """
        # Build request from kwargs if not provided
        if request is None:
            # Handle raw_data - can be string or dict
            final_raw_data: dict[str, Any] = {}

            if payload is not None and raw_data is not None:
                raise ValueError("Provide either payload or raw_data, not both")
            
            if payload is not None:
                final_raw_data = payload
            elif raw_data is not None:
                if isinstance(raw_data, str):
                    import json
                    try:
                        final_raw_data = json.loads(raw_data)
                    except json.JSONDecodeError:
                        final_raw_data = {"raw": raw_data}
                else:
                    final_raw_data = raw_data
            
            request = EventIngestRequest(
                timestamp=timestamp or datetime.now(timezone.utc),
                source_ip=source_ip or "0.0.0.0",
                dest_ip=dest_ip or "0.0.0.0",
                source_port=source_port,
                dest_port=dest_port,
                protocol=protocol or "TCP",
                event_type=event_type or "unknown",
                raw_data=final_raw_data,
            )
        
        # Create event record
        event = Event(
            id=uuid.uuid4(),
            timestamp=request.timestamp,
            source_ip=request.source_ip,
            dest_ip=request.dest_ip,
            source_port=request.source_port,
            dest_port=request.dest_port,
            protocol=request.protocol,
            event_type=request.event_type,
            raw_data=request.raw_data,
            created_at=datetime.now(timezone.utc),
        )
        
        self.db.add(event)
        await self.db.flush()
        
        # Return the Event for pipeline chaining (tests need this)
        # Also accessible via event.id for the response
        return event
    
    async def get_event(self, event_id: uuid.UUID) -> Event | None:
        """Get a single event by ID."""
        result = await self.db.execute(
            select(Event).where(Event.id == event_id)
        )
        return result.scalar_one_or_none()
    
    async def list_events(
        self,
        limit: int = 50,
        offset: int = 0,
        event_type: str | None = None,
        start_time: datetime | None = None,
        end_time: datetime | None = None,
    ) -> tuple[list[Event], int]:
        """List events with filters and pagination."""
        query = select(Event)
        count_query = select(Event)
        
        # Apply filters
        if event_type:
            query = query.where(Event.event_type == event_type)
            count_query = count_query.where(Event.event_type == event_type)
        
        if start_time:
            query = query.where(Event.timestamp >= start_time)
            count_query = count_query.where(Event.timestamp >= start_time)
        
        if end_time:
            query = query.where(Event.timestamp <= end_time)
            count_query = count_query.where(Event.timestamp <= end_time)
        
        # Get total count
        from sqlalchemy import func
        count_result = await self.db.execute(
            select(func.count()).select_from(count_query.subquery())
        )
        total = count_result.scalar() or 0
        
        # Apply pagination and ordering
        query = query.order_by(Event.created_at.desc()).offset(offset).limit(limit)
        
        result = await self.db.execute(query)
        events = list(result.scalars().all())
        
        return events, total

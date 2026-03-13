"""
NSA-X Layer 2: Event Processing Service
Normalizes and enriches events - NO detection logic here.
"""
import hashlib
import logging
import time
import uuid
from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Event, ProcessedEvent


logger = logging.getLogger(__name__)


class ProcessingService:
    """Layer 2: Event normalization and enrichment."""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def process_event(self, event: Event) -> ProcessedEvent:
        """
        Process and enrich a raw event.
        
        Critical Rules:
        - NO detection logic here
        - NO rule evaluation
        - Only transformation and enrichment
        - Must complete in <100ms per event
        - If enrichment fails, store partial data (don't block)
        """
        start_time = time.time()
        
        # Build normalized structure
        parsed_fields = self._normalize_event(event)
        
        # Enrich with context (mocked for MVP)
        # Wrap in try/except to ensure partial data is stored on failure
        try:
            hostname = self._lookup_hostname(event.source_ip)
            criticality = self._calculate_criticality(event.source_ip, event.dest_ip)
        except Exception as exc:
            logger.warning(
                "Processing enrichment failed, using fallback values",
                extra={"event_id": str(event.id), "error": str(exc)},
            )
            hostname = "unknown"
            criticality = 50
        
        # Calculate event hash for deduplication
        event_hash = self._calculate_event_hash(event)
        
        # Calculate processing duration
        duration_ms = int((time.time() - start_time) * 1000)
        
        # Create processed event
        processed = ProcessedEvent(
            id=uuid.uuid4(),
            event_id=event.id,
            parsed_fields=parsed_fields,
            asset_hostname=hostname,
            asset_criticality=criticality,
            event_hash=event_hash,
            processing_timestamp=datetime.now(timezone.utc),
            processing_duration_ms=duration_ms,
        )
        
        self.db.add(processed)
        await self.db.flush()
        
        return processed
    
    def _normalize_event(self, event: Event) -> dict:
        """Normalize event into standard structure."""
        timestamp = event.timestamp
        hour_of_day = timestamp.hour
        day_of_week = timestamp.weekday()
        
        # Business hours: 9 AM - 6 PM (9 <= hour < 18), Monday-Friday
        is_business_hours = (
            0 <= day_of_week <= 4 and  # Monday-Friday
            9 <= hour_of_day < 18       # 9 AM - 5:59 PM (6 PM excluded)
        )
        
        return {
            "event_type": event.event_type,  # Include event type for rule evaluation
            "network": {
                "source": {
                    "ip": str(event.source_ip),
                    "port": event.source_port,
                },
                "destination": {
                    "ip": str(event.dest_ip),
                    "port": event.dest_port,
                },
                "protocol": event.protocol,
            },
            "temporal": {
                "timestamp": timestamp.isoformat(),
                "hour_of_day": hour_of_day,
                "day_of_week": day_of_week,
                "is_business_hours": is_business_hours,
            },
            "asset": {
                "hostname": None,  # Will be enriched
                "criticality": 50,  # Default, will be enriched
            },
        }
    
    def _lookup_hostname(self, ip: str) -> str:
        """
        Mock hostname lookup from IP.
        In production: DNS reverse lookup or CMDB query.
        """
        # Generate deterministic hostname from IP
        ip_parts = str(ip).split(".")
        if len(ip_parts) == 4:
            # IPv4
            prefix = "host"
            if ip_parts[0] == "10":
                prefix = "internal"
            elif ip_parts[0] == "192" and ip_parts[1] == "168":
                prefix = "local"
            elif ip_parts[0] in ("172",) and 16 <= int(ip_parts[1]) <= 31:
                prefix = "private"
            else:
                prefix = "external"
            return f"{prefix}-{ip_parts[2]}-{ip_parts[3]}.nsax.local"
        else:
            # IPv6 or other - use hashlib for proper hashing
            ip_hash = int(hashlib.md5(str(ip).encode()).hexdigest()[:8], 16) % 10000
            return f"host-{ip_hash}.nsax.local"
    
    def _calculate_criticality(self, source_ip: str, dest_ip: str) -> int:
        """
        Mock asset criticality calculation.
        In production: CMDB lookup or asset inventory query.
        Returns 1-100.
        """
        # Hash-based deterministic criticality
        combined = f"{source_ip}:{dest_ip}"
        hash_value = int(hashlib.md5(combined.encode()).hexdigest()[:8], 16)
        
        # Map to 1-100 range with some distribution
        base_criticality = (hash_value % 100) + 1
        
        # Boost criticality for internal assets (includes all RFC1918 ranges)
        dest_str = str(dest_ip)
        if (
            dest_str.startswith("10.") or 
            dest_str.startswith("192.168.") or
            self._is_172_private(dest_str)
        ):
            base_criticality = min(100, base_criticality + 20)
        
        return base_criticality
    
    def _is_172_private(self, ip: str) -> bool:
        """Check if IP is in 172.16.0.0/12 range (172.16-31.x.x)."""
        if not ip.startswith("172."):
            return False
        parts = ip.split(".")
        if len(parts) < 2:
            return False
        try:
            second_octet = int(parts[1])
            return 16 <= second_octet <= 31
        except ValueError:
            return False
    
    def _calculate_event_hash(self, event: Event) -> str:
        """Calculate SHA-256 hash for event deduplication."""
        hash_input = (
            f"{event.source_ip}|{event.dest_ip}|"
            f"{event.source_port}|{event.dest_port}|"
            f"{event.protocol}|{event.event_type}|"
            f"{event.timestamp.isoformat()}"
        )
        return hashlib.sha256(hash_input.encode()).hexdigest()
    
    async def get_processed_event(self, event_id: uuid.UUID) -> ProcessedEvent | None:
        """Get processed event by original event ID."""
        result = await self.db.execute(
            select(ProcessedEvent).where(ProcessedEvent.event_id == event_id)
        )
        return result.scalar_one_or_none()
    
    async def get_processed_event_by_id(self, processed_id: uuid.UUID) -> ProcessedEvent | None:
        """Get processed event by its own ID."""
        result = await self.db.execute(
            select(ProcessedEvent).where(ProcessedEvent.id == processed_id)
        )
        return result.scalar_one_or_none()

"""
NSA-X Layer 3: Neural Detection Service
Detects anomalies using pattern analysis (rule-based approximation for MVP).
"""
import hashlib
import uuid
from datetime import datetime, timedelta, timezone

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Event, NeuralDetection, ProcessedEvent

# Model version for tracking
MODEL_VERSION = "rule-based-v1"


class NeuralDetectionService:
    """Layer 3: Anomaly detection using pattern analysis."""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def detect_anomalies(self, processed_event: ProcessedEvent) -> NeuralDetection:
        """
        Detect anomalies in a processed event.
        
        Critical Rules:
        - NO explanations generated here (just scores)
        - NO policy checks
        - NO decisions
        - All scores must be 0.0 to 1.0 range
        - Must complete in <200ms per event
        """
        # Get original event
        event_result = await self.db.execute(
            select(Event).where(Event.id == processed_event.event_id)
        )
        event = event_result.scalar_one()
        
        parsed = processed_event.parsed_fields or {}
        
        # Calculate individual anomaly scores
        frequency_score = await self._calculate_frequency_anomaly(event)
        port_score = self._calculate_port_anomaly(event)
        temporal_score = self._calculate_temporal_anomaly(parsed)
        geographic_score = self._calculate_geographic_anomaly(event)
        
        # Weighted composite score
        anomaly_score = (
            0.3 * frequency_score +
            0.3 * port_score +
            0.2 * temporal_score +
            0.2 * geographic_score
        )
        
        # Clamp to 0.0-1.0 range
        anomaly_score = max(0.0, min(1.0, anomaly_score))
        
        # Create detection record
        detection = NeuralDetection(
            id=uuid.uuid4(),
            processed_event_id=processed_event.id,
            anomaly_score=round(anomaly_score, 2),
            frequency_score=round(frequency_score, 2),
            port_score=round(port_score, 2),
            temporal_score=round(temporal_score, 2),
            geographic_score=round(geographic_score, 2),
            detection_timestamp=datetime.now(timezone.utc),
            model_version=MODEL_VERSION,
        )
        
        self.db.add(detection)
        await self.db.flush()
        
        return detection
    
    async def _calculate_frequency_anomaly(self, event: Event) -> float:
        """
        Calculate frequency anomaly score.
        Higher score = more unusual event frequency from this source.
        """
        # Count events from this source IP in last 24 hours
        cutoff = datetime.now(timezone.utc) - timedelta(hours=24)
        
        result = await self.db.execute(
            select(func.count(Event.id))
            .where(Event.source_ip == event.source_ip)
            .where(Event.created_at >= cutoff)
        )
        event_count = result.scalar() or 0
        
        # Scoring logic:
        # 0-5 events: normal (low score)
        # 6-20 events: slightly elevated
        # 21-50 events: elevated
        # 51-100 events: high
        # 100+ events: very high (potential attack)
        
        if event_count <= 5:
            return 0.1
        elif event_count <= 20:
            return 0.3
        elif event_count <= 50:
            return 0.5
        elif event_count <= 100:
            return 0.7
        else:
            return 0.9
    
    def _calculate_port_anomaly(self, event: Event) -> float:
        """
        Calculate port anomaly score.
        Higher score = more unusual port usage.
        """
        dest_port = event.dest_port
        
        if dest_port is None:
            return 0.2  # Unknown port

        common_ports = {22, 80, 443, 53, 25, 110, 143, 993, 995}
        db_ports = {3306, 5432, 1433, 27017, 6379}  # MySQL, PostgreSQL, MSSQL, MongoDB, Redis

        if dest_port in common_ports:
            return 0.1  # Very common
        if dest_port in db_ports:
            return 0.4  # Database access is noteworthy
        
        # Well-known ports (0-1023) are generally safer
        if dest_port <= 1023:
            return 0.3  # Less common but still well-known range
        
        # Registered ports (1024-49151)
        elif dest_port <= 49151:
            # Some common application ports
            app_ports = {3389, 5900, 8080, 8443, 8000, 8888}
            if dest_port in app_ports:
                return 0.4  # Common but noteworthy
            
            # High ports often used by malware
            if dest_port >= 8000:
                return 0.7  # Suspicious
            return 0.5
        
        # Dynamic/ephemeral ports (49152-65535)
        else:
            return 0.8  # Unusual for destination
    
    def _calculate_temporal_anomaly(self, parsed_fields: dict) -> float:
        """
        Calculate temporal anomaly score.
        Higher score = more unusual time of activity.
        """
        temporal = parsed_fields.get("temporal", {})
        hour = temporal.get("hour_of_day", 12)
        day = temporal.get("day_of_week", 2)
        is_business = temporal.get("is_business_hours", True)
        
        # Weekend activity is more suspicious
        if day >= 5:  # Saturday or Sunday
            base_score = 0.6
        else:
            base_score = 0.2
        
        # Night hours (10 PM - 6 AM) are more suspicious
        if hour >= 22 or hour <= 6:
            base_score += 0.3
        
        # Outside business hours is slightly suspicious
        if not is_business:
            base_score += 0.1
        
        return min(1.0, base_score)
    
    def _calculate_geographic_anomaly(self, event: Event) -> float:
        """
        Calculate geographic anomaly score (mocked for MVP).
        Higher score = more unusual location.
        """
        source_ip = str(event.source_ip)
        dest_ip = str(event.dest_ip)
        
        # Internal IP ranges are considered "home" geography
        internal_prefixes = ("10.", "192.168.", "172.16.", "172.17.", "172.18.",
                            "172.19.", "172.20.", "172.21.", "172.22.", "172.23.",
                            "172.24.", "172.25.", "172.26.", "172.27.", "172.28.",
                            "172.29.", "172.30.", "172.31.")
        
        source_internal = any(source_ip.startswith(p) for p in internal_prefixes)
        dest_internal = any(dest_ip.startswith(p) for p in internal_prefixes)
        
        # Internal to internal: safe
        if source_internal and dest_internal:
            return 0.1
        
        # Internal to external: moderate concern
        if source_internal and not dest_internal:
            # Certain external ranges are more suspicious
            # Using IP hash to simulate geo-lookup
            ip_hash = int(hashlib.md5(dest_ip.encode()).hexdigest()[:4], 16)
            if ip_hash % 10 < 2:  # 20% chance of "suspicious" geography
                return 0.8
            return 0.4
        
        # External to internal: concerning
        if not source_internal and dest_internal:
            return 0.7
        
        # External to external: unusual (why would we see this?)
        return 0.6
    
    async def get_detection(self, processed_event_id: uuid.UUID) -> NeuralDetection | None:
        """Get detection result for a processed event."""
        result = await self.db.execute(
            select(NeuralDetection).where(
                NeuralDetection.processed_event_id == processed_event_id
            )
        )
        return result.scalar_one_or_none()

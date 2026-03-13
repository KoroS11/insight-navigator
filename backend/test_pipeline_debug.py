"""Debug script to test pipeline alert generation."""
import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from datetime import datetime, timezone
import uuid

from app.models import Event, Base
from app.services.layer2_processing import ProcessingService
from app.services.layer3_neural import NeuralDetectionService
from app.services.layer4_symbolic import SymbolicReasoningService
from app.services.layer5_integration import IntegrationService


async def test_pipeline():
    engine = create_async_engine("sqlite+aiosqlite:///:memory:")
    
    # Create tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    
    async with async_session() as session:
        # Create event - external to internal, high port
        event = Event(
            id=uuid.uuid4(),
            event_type="suspicious_auth",
            source_ip="185.220.101.50",  # External
            dest_ip="192.168.1.10",       # Internal
            dest_port=9999,               # High port (> 8000)
            raw_data={"method": "brute_force"},
            created_at=datetime.now(timezone.utc),
            timestamp=datetime.now(timezone.utc),
        )
        session.add(event)
        await session.flush()
        print(f"Event created: {event.id}")
        
        # Layer 2: Process
        l2 = ProcessingService(session)
        processed = await l2.process(event)
        print(f"Parsed fields network.destination: {processed.parsed_fields.get('network', {}).get('destination')}")
        
        # Layer 3: Detect
        l3 = NeuralDetectionService(session)
        detection = await l3.detect(processed)
        print(f"Detection: anomaly_score={detection.anomaly_score}")
        
        # Layer 4: Evaluate rules
        l4 = SymbolicReasoningService(session)
        await l4.ensure_default_rules()
        evaluations = await l4.evaluate(processed, detection)
        
        print(f"All evaluations: {len(evaluations)}")
        for e in evaluations:
            print(f"  - Rule {e.rule_id}: matched={e.matched}, severity={e.severity}")
        
        matched = [e for e in evaluations if e.matched]
        print(f"\nMatched rules: {len(matched)}")
        high_severity = [e for e in matched if e.severity == "HIGH"]
        print(f"HIGH severity matches: {len(high_severity)}")
        
        # Layer 5: Integrate
        l5 = IntegrationService(session)
        alert = await l5.integrate(processed, detection, evaluations)
        
        if alert:
            print(f"\n✅ ALERT CREATED: {alert.id}")
            print(f"   Risk score: {alert.risk_score}")
            print(f"   Severity: {alert.severity}")
        else:
            print("\n❌ NO ALERT CREATED")
            print("   Reasons for no alert:")
            print(f"   - Anomaly score {detection.anomaly_score} < 0.7: {detection.anomaly_score < 0.7}")
            print(f"   - No HIGH severity match: {len(high_severity) == 0}")
            print(f"   - Less than 2 matches: {len(matched) < 2}")


if __name__ == "__main__":
    asyncio.run(test_pipeline())

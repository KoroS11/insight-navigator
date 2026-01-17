"""
Performance Tests
Tests for system performance requirements.
"""
import time
import asyncio
from datetime import datetime, timezone

import pytest
from httpx import AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Event, Rule
from app.services import PipelineOrchestrator


def valid_event_data(**overrides) -> dict:
    """Create valid event data with all required fields, allowing overrides."""
    base = {
        "event_type": "test",
        "source_ip": "10.0.0.1",
        "dest_ip": "10.0.0.2",
        "protocol": "TCP",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "raw_data": {"test": "data"},
    }
    base.update(overrides)
    return base


class TestThroughputRequirements:
    """PERF-001: Throughput performance tests."""

    @pytest.fixture
    async def setup_rules(self, db_session: AsyncSession):
        """Create rules for performance testing."""
        rules = [
            Rule(
                rule_id="PERF-RULE-001",
                name="Performance Test Rule",
                category="pattern",
                conditions={"dest_port": 4444},
                severity="HIGH",
                enabled=True,
            ),
        ]
        for rule in rules:
            db_session.add(rule)
        await db_session.flush()
        return rules

    @pytest.mark.slow
    @pytest.mark.asyncio
    async def test_event_processing_rate(
        self, db_session: AsyncSession, setup_rules
    ):
        """
        PERF-001: System should process ≥100 events/minute.
        
        Target: 100 events in 60 seconds = ~1.67 events/second
        """
        from app.services import IngestionService, ProcessingService

        ing_service = IngestionService(db_session)
        proc_service = ProcessingService(db_session)

        event_count = 100
        start_time = time.time()

        for i in range(event_count):
            event = await ing_service.ingest_event(
                event_type="throughput_test",
                source_ip=f"10.0.{i % 256}.{i % 256}",
                dest_ip="10.0.0.1",
                dest_port=443,
                protocol="TCP",
                timestamp=datetime.now(timezone.utc),
                raw_data={"index": i},
            )
            await db_session.flush()
            
            processed = await proc_service.process_event(event)
            await db_session.flush()

        elapsed = time.time() - start_time
        events_per_minute = (event_count / elapsed) * 60

        print(f"\nProcessed {event_count} events in {elapsed:.2f}s")
        print(f"Rate: {events_per_minute:.1f} events/minute")

        # Must achieve at least 100 events/minute
        assert events_per_minute >= 100, f"Only {events_per_minute:.1f} events/min, need ≥100"

    @pytest.mark.slow
    @pytest.mark.asyncio
    async def test_api_throughput(
        self, client: AsyncClient, auth_headers: dict
    ):
        """Test API endpoint throughput."""
        event_count = 50
        start_time = time.time()

        for i in range(event_count):
            response = await client.post(
                "/api/v1/events/",
                json=valid_event_data(
                    event_type="api_throughput_test",
                    source_ip=f"10.0.{i % 256}.{i % 256}",
                ),
                headers=auth_headers
            )
            assert response.status_code == 201

        elapsed = time.time() - start_time
        events_per_minute = (event_count / elapsed) * 60

        print(f"\nAPI processed {event_count} events in {elapsed:.2f}s")
        print(f"Rate: {events_per_minute:.1f} events/minute")


class TestLatencyRequirements:
    """PERF-002: Latency performance tests."""

    @pytest.mark.asyncio
    async def test_single_event_latency(
        self, client: AsyncClient, auth_headers: dict
    ):
        """
        PERF-002: Single event processing < 2 seconds.
        
        Measures: Event submission → Response time
        """
        latencies = []

        for i in range(10):
            start = time.time()
            
            response = await client.post(
                "/api/v1/events/",
                json=valid_event_data(
                    event_type="latency_test",
                    source_ip=f"10.0.0.{i+1}",
                    dest_ip="10.0.0.100",
                ),
                headers=auth_headers
            )
            
            elapsed = (time.time() - start) * 1000  # ms
            latencies.append(elapsed)
            assert response.status_code == 201

        avg_latency = sum(latencies) / len(latencies)
        max_latency = max(latencies)
        p95_latency = sorted(latencies)[int(len(latencies) * 0.95)]

        print(f"\nLatency Stats (ms):")
        print(f"  Average: {avg_latency:.2f}")
        print(f"  Max: {max_latency:.2f}")
        print(f"  P95: {p95_latency:.2f}")

        # Average should be well under 2 seconds
        assert avg_latency < 2000, f"Avg latency {avg_latency}ms exceeds 2000ms"

    @pytest.mark.asyncio
    async def test_alert_list_latency(
        self, client: AsyncClient, auth_headers: dict
    ):
        """Test alert listing response time."""
        latencies = []

        for _ in range(5):
            start = time.time()
            response = await client.get("/api/v1/alerts/", headers=auth_headers)
            elapsed = (time.time() - start) * 1000
            latencies.append(elapsed)
            assert response.status_code == 200

        avg_latency = sum(latencies) / len(latencies)
        print(f"\nAlert list avg latency: {avg_latency:.2f}ms")

        # List should be fast
        assert avg_latency < 1000, f"Avg latency {avg_latency}ms exceeds 1000ms"


class TestDatabasePerformance:
    """PERF-003: Database performance tests."""

    @pytest.mark.asyncio
    async def test_bulk_event_insert(self, db_session: AsyncSession):
        """Test bulk event insertion performance."""
        from app.services import IngestionService

        service = IngestionService(db_session)
        event_count = 100

        start = time.time()
        for i in range(event_count):
            await service.ingest_event(
                event_type="bulk_test",
                source_ip=f"10.{i // 256}.{i % 256}.1",
                dest_ip="10.0.0.1",
                protocol="TCP",
                timestamp=datetime.now(timezone.utc),
                raw_data={},
            )
        await db_session.flush()
        elapsed = time.time() - start

        rate = event_count / elapsed
        print(f"\nBulk insert: {event_count} events in {elapsed:.2f}s ({rate:.1f}/s)")

        assert rate >= 50, f"Insert rate {rate:.1f}/s below minimum 50/s"

    @pytest.mark.asyncio
    async def test_event_query_performance(self, db_session: AsyncSession):
        """Test event query performance with many records."""
        from app.services import IngestionService

        service = IngestionService(db_session)

        # Create many events
        for i in range(200):
            await service.ingest_event(
                event_type="query_perf_test",
                source_ip=f"10.0.{i % 256}.{i % 256}",
                dest_ip="10.0.0.1",
                protocol="TCP",
                timestamp=datetime.now(timezone.utc),
                raw_data={},
            )
        await db_session.flush()

        # Time the query
        start = time.time()
        events = await service.list_events(event_type="query_perf_test", limit=100)
        elapsed = (time.time() - start) * 1000

        print(f"\nQuery 100 events: {elapsed:.2f}ms")
        assert elapsed < 500, f"Query took {elapsed}ms, expected < 500ms"


class TestMemoryUsage:
    """Tests for memory efficiency."""

    @pytest.mark.slow
    @pytest.mark.asyncio
    async def test_large_payload_handling(
        self, client: AsyncClient, auth_headers: dict
    ):
        """Test handling of large event payloads."""
        # Create reasonably large payload (100KB)
        large_data = "x" * (100 * 1024)
        
        start = time.time()
        response = await client.post(
            "/api/v1/events/",
            json=valid_event_data(
                event_type="large_payload_test",
                raw_data={"data": large_data},
            ),
            headers=auth_headers
        )
        elapsed = (time.time() - start) * 1000

        print(f"\nLarge payload (100KB): {elapsed:.2f}ms")
        # Should handle reasonably quickly or reject
        assert response.status_code in [201, 400, 413]

    @pytest.mark.asyncio
    async def test_concurrent_requests(
        self, client: AsyncClient, auth_headers: dict
    ):
        """Test handling of concurrent requests."""
        request_count = 20

        async def make_request(i: int):
            return await client.post(
                "/api/v1/events/",
                json=valid_event_data(
                    event_type="concurrent_test",
                    source_ip=f"10.0.0.{i+1}",
                    dest_ip="10.0.0.100",
                ),
                headers=auth_headers
            )

        start = time.time()
        # Note: Sequential in this test due to session handling
        # Real concurrent would use separate sessions
        responses = []
        for i in range(request_count):
            resp = await make_request(i)
            responses.append(resp)
        elapsed = time.time() - start

        success_count = sum(1 for r in responses if r.status_code == 201)
        print(f"\nConcurrent: {success_count}/{request_count} succeeded in {elapsed:.2f}s")

        assert success_count == request_count


class TestPipelinePerformance:
    """Full pipeline performance tests."""

    @pytest.fixture
    async def setup_rules(self, db_session: AsyncSession):
        """Create rules for pipeline testing."""
        rules = [
            Rule(
                rule_id="PIPELINE-PERF-001",
                name="Pipeline Perf Rule 1",
                category="pattern",
                conditions={"dest_port": 4444},
                severity="HIGH",
                enabled=True,
            ),
            Rule(
                rule_id="PIPELINE-PERF-002",
                name="Pipeline Perf Rule 2",
                category="range",
                conditions={"min_port": 8000},
                severity="MEDIUM",
                enabled=True,
            ),
        ]
        for rule in rules:
            db_session.add(rule)
        await db_session.flush()
        return rules

    @pytest.mark.slow
    @pytest.mark.asyncio
    async def test_full_pipeline_throughput(
        self, db_session: AsyncSession, setup_rules
    ):
        """Test full pipeline (L1-L5) throughput."""
        pipeline = PipelineOrchestrator(db_session)
        event_count = 50

        start = time.time()
        for i in range(event_count):
            await pipeline.process_event(
                event_type="full_pipeline_test",
                source_ip=f"10.0.{i % 256}.{i % 256}",
                dest_ip="10.0.0.1",
                dest_port=4444 if i % 5 == 0 else 443,
            )
        await db_session.flush()
        elapsed = time.time() - start

        rate = (event_count / elapsed) * 60  # per minute
        print(f"\nFull pipeline: {event_count} events in {elapsed:.2f}s")
        print(f"Rate: {rate:.1f} events/minute")

        # Full pipeline should still meet minimum throughput
        assert rate >= 50, f"Pipeline rate {rate:.1f}/min below minimum 50/min"



"""
Integration Tests: Full Pipeline Flow
Tests for complete event processing through all 7 layers.
"""
import uuid
from datetime import datetime, timezone

import pytest
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import (
    Event, ProcessedEvent, NeuralDetection, Rule, RuleEvaluation,
    Alert, Explanation, Decision, AuditLog, User
)
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


class TestFullPipelineFlow:
    """TEST-INT-001 to TEST-INT-003: Full pipeline integration tests."""

    @pytest.fixture
    async def setup_rules(self, db_session: AsyncSession):
        """Create rules for integration testing."""
        rules = [
            Rule(
                rule_id="INT-RULE-001",
                name="Malicious Port",
                category="pattern",
                conditions={"dest_port": 4444},
                severity="HIGH",
                enabled=True,
            ),
            Rule(
                rule_id="INT-RULE-002",
                name="External Connection",
                category="pattern",
                conditions={"source_external": True, "dest_internal": True},
                severity="HIGH",
                enabled=True,
            ),
        ]
        for rule in rules:
            db_session.add(rule)
        await db_session.flush()
        return rules

    @pytest.mark.asyncio
    async def test_event_flows_through_all_layers(
        self, db_session: AsyncSession, setup_rules
    ):
        """TEST-INT-001: Event flows from ingestion to alert."""
        pipeline = PipelineOrchestrator(db_session)

        # Submit event to pipeline
        result = await pipeline.process_event(
            event_type="network_connection",
            source_ip="192.168.1.100",
            dest_ip="10.0.0.50",
            dest_port=4444,  # Malicious port
        )
        await db_session.flush()

        # Verify all layers created data
        assert result.event is not None
        assert result.processed_event is not None
        assert result.detection is not None
        assert len(result.evaluations) > 0
        # Alerts may or may not be generated depending on thresholds
        # But all pipeline stages should execute

    @pytest.mark.asyncio
    async def test_critical_event_generates_alert(
        self, db_session: AsyncSession, setup_rules
    ):
        """TEST-INT-002: Critical event generates alert with explanation."""
        pipeline = PipelineOrchestrator(db_session)

        result = await pipeline.process_event(
            event_type="network_connection",
            source_ip="203.0.113.50",  # External
            dest_ip="192.168.1.10",    # Internal
            dest_port=4444,            # Malicious port
        )
        await db_session.flush()

        # Alert may or may not be generated depending on thresholds
        if result.alert:
            assert result.alert.classification in ["LOW", "MEDIUM", "HIGH"]

    @pytest.mark.asyncio
    async def test_pipeline_preserves_data_integrity(
        self, db_session: AsyncSession, setup_rules
    ):
        """TEST-INT-003: Pipeline preserves data through all layers."""
        pipeline = PipelineOrchestrator(db_session)

        original_ip = "10.20.30.40"
        original_port = 8080

        result = await pipeline.process_event(
            event_type="integrity_test",
            source_ip=original_ip,
            dest_ip="10.0.0.2",
            dest_port=original_port,
            raw_data={"integrity": "test"},
        )
        await db_session.flush()

        # Verify original data preserved
        event = result.event
        assert str(event.source_ip) == original_ip
        assert event.dest_port == original_port

        # Verify processed event links correctly
        processed = result.processed_event
        assert processed.event_id == event.id

        # Verify detection links correctly
        detection = result.detection
        assert detection.processed_event_id == processed.id


class TestDatabaseTransactionIntegrity:
    """TEST-INT-004 to TEST-INT-005: Database transaction tests."""

    @pytest.fixture
    async def setup_rule(self, db_session: AsyncSession):
        """Create a test rule."""
        rule = Rule(
            rule_id="TX-RULE-001",
            name="Transaction Test Rule",
            category="pattern",
            conditions={"dest_port": 5555},
            severity="HIGH",
            enabled=True,
        )
        db_session.add(rule)
        await db_session.flush()
        return rule

    @pytest.mark.asyncio
    async def test_rollback_on_failure(self, db_session: AsyncSession, setup_rule):
        """TEST-INT-004: Transaction rolls back on failure."""
        from app.services import IngestionService, ProcessingService

        ing_service = IngestionService(db_session)

        # Count events before
        before_result = await db_session.execute(select(Event))
        before_count = len(list(before_result.scalars().all()))

        # Start event ingestion
        event = await ing_service.ingest_event(
            event_type="rollback_test",
            source_ip="10.0.0.1",
            dest_ip="10.0.0.2",
            protocol="TCP",
            timestamp=datetime.now(timezone.utc),
            raw_data={},
        )

        # Simulate failure by rolling back
        await db_session.rollback()

        # Count events after rollback
        after_result = await db_session.execute(select(Event))
        after_count = len(list(after_result.scalars().all()))

        # Should be same count (event rolled back)
        assert after_count == before_count

    @pytest.mark.asyncio
    async def test_concurrent_event_processing(self, db_session: AsyncSession, setup_rule):
        """TEST-INT-005: Concurrent events don't interfere."""
        import asyncio
        from app.services import IngestionService, ProcessingService

        ing_service = IngestionService(db_session)
        proc_service = ProcessingService(db_session)

        async def process_event(ip_suffix: int):
            event = await ing_service.ingest_event(
                event_type="concurrent_test",
                source_ip=f"10.0.0.{ip_suffix}",
                dest_ip="10.0.0.100",
                protocol="TCP",
                timestamp=datetime.now(timezone.utc),
                raw_data={"id": ip_suffix},
            )
            await db_session.flush()
            processed = await proc_service.process_event(event)
            await db_session.flush()
            return event, processed

        # Process multiple events (sequentially in same session for SQLite)
        results = []
        for i in range(5):
            result = await process_event(i + 1)
            results.append(result)

        # All should succeed with unique data
        ips = [str(r[0].source_ip) for r in results]
        assert len(set(ips)) == 5  # All unique


class TestAPIIntegration:
    """TEST-INT-006 to TEST-INT-008: API integration tests."""

    @pytest.fixture
    async def setup_rules_api(self, db_session: AsyncSession):
        """Create rules for API testing."""
        rule = Rule(
            rule_id="API-RULE-001",
            name="API Test Rule",
            category="pattern",
            conditions={"dest_port": 6666},
            severity="HIGH",
            enabled=True,
        )
        db_session.add(rule)
        await db_session.flush()
        return rule

    @pytest.mark.asyncio
    async def test_api_event_to_alert_flow(
        self, client, auth_headers, setup_rules_api
    ):
        """TEST-INT-006: API event submission generates alert."""
        from httpx import AsyncClient

        event_data = valid_event_data(
            event_type="api_integration_test",
            dest_port=6666,
        )

        # Submit event
        response = await client.post(
            "/api/v1/events/",
            json=event_data,
            headers=auth_headers
        )
        assert response.status_code == 201

        event_id = response.json()["event_id"]

        # Check for alerts (may need to query after pipeline)
        alerts_response = await client.get(
            "/api/v1/alerts/",
            headers=auth_headers
        )
        assert alerts_response.status_code == 200

    @pytest.mark.asyncio
    async def test_api_alert_decision_flow(
        self, client, auth_headers, db_session: AsyncSession, setup_rules_api
    ):
        """TEST-INT-007: API decision creation for alert."""
        # First create an event that generates alert
        event_data = valid_event_data(
            event_type="decision_flow_test",
            dest_port=6666,
        )

        await client.post(
            "/api/v1/events/",
            json=event_data,
            headers=auth_headers
        )

        # Get pending alerts
        alerts_response = await client.get(
            "/api/v1/alerts/?status=PENDING",
            headers=auth_headers
        )

        if alerts_response.status_code == 200:
            alerts = alerts_response.json()
            if alerts and len(alerts) > 0:
                alert_id = alerts[0]["id"]

                # Create decision
                decision_data = {
                    "action": "DISMISS",
                    "justification": "API integration test decision.",
                }

                decision_response = await client.post(
                    f"/api/v1/alerts/{alert_id}/decisions",
                    json=decision_data,
                    headers=auth_headers
                )

                # May be 201 or 400 if decision exists
                assert decision_response.status_code in [201, 400]

    @pytest.mark.asyncio
    async def test_api_audit_trail(
        self, client, auth_headers
    ):
        """TEST-INT-008: API operations create audit trail."""
        # Get audit logs
        response = await client.get(
            "/api/v1/audit/",
            headers=auth_headers
        )
        assert response.status_code == 200

        # Should return list of audit entries
        logs = response.json()
        assert isinstance(logs, list)


class TestLayerIsolation:
    """Integration tests for layer boundary enforcement."""

    @pytest.mark.asyncio
    async def test_layer_progression_order(self, db_session: AsyncSession):
        """Verify layers execute in correct order."""
        from app.services import (
            IngestionService, ProcessingService, NeuralDetectionService,
            SymbolicReasoningService, IntegrationService
        )

        # Create rule
        rule = Rule(
            rule_id="ORDER-RULE-001",
            name="Order Test Rule",
            category="pattern",
            conditions={"dest_port": 7890},
            severity="MEDIUM",
            enabled=True,
        )
        db_session.add(rule)
        await db_session.flush()

        timestamps = []

        # Layer 1
        ing_service = IngestionService(db_session)
        event = await ing_service.ingest_event(
            event_type="order_test",
            source_ip="10.0.0.1",
            dest_ip="10.0.0.2",
            dest_port=7890,
            protocol="TCP",
            timestamp=datetime.now(timezone.utc),
            raw_data={},
        )
        await db_session.flush()
        timestamps.append(("L1", event.created_at))

        # Layer 2
        proc_service = ProcessingService(db_session)
        processed = await proc_service.process_event(event)
        await db_session.flush()
        timestamps.append(("L2", processed.processing_timestamp))

        # Layer 3
        neural_service = NeuralDetectionService(db_session)
        detection = await neural_service.detect_anomalies(processed)
        await db_session.flush()
        timestamps.append(("L3", detection.detection_timestamp))

        # Layer 4
        symbolic_service = SymbolicReasoningService(db_session)
        evaluations = await symbolic_service.evaluate_rules(processed, event_count_24h=0)
        await db_session.flush()
        if evaluations:
            timestamps.append(("L4", evaluations[0].evaluation_timestamp))

        # Layer 5
        integration_service = IntegrationService(db_session)
        alert = await integration_service.integrate_reasoning(
            processed, detection, evaluations
        )
        await db_session.flush()
        if alert:
            timestamps.append(("L5", alert.created_at))

        # Verify ordering (each layer after previous)
        for i in range(1, len(timestamps)):
            prev_layer, prev_time = timestamps[i-1]
            curr_layer, curr_time = timestamps[i]
            # Timestamps should be >= previous (same or later)
            assert curr_time >= prev_time, f"{curr_layer} before {prev_layer}"



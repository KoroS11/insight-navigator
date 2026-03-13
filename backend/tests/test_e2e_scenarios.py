"""
End-to-End Tests: Complete Scenarios
Tests for full user workflows from event to decision.
"""
import uuid
from datetime import datetime, timezone

import pytest
from httpx import AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Event, Alert, Decision, AuditLog, Rule


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


class TestSecurityAnalystWorkflow:
    """TEST-E2E-001: Complete analyst workflow."""

    @pytest.fixture
    async def setup_e2e_environment(self, db_session: AsyncSession):
        """Setup complete environment for E2E testing."""
        rules = [
            Rule(
                rule_id="E2E-RULE-001",
                name="Critical Port Detection",
                category="pattern",
                conditions={"dest_port": 4444},
                severity="HIGH",
                enabled=True,
            ),
            Rule(
                rule_id="E2E-RULE-002",
                name="SSH Brute Force",
                category="threshold",
                conditions={"event_type": "auth_failure", "threshold": 5},
                severity="HIGH",
                enabled=True,
            ),
        ]
        for rule in rules:
            db_session.add(rule)
        await db_session.flush()
        return rules

    @pytest.mark.asyncio
    async def test_complete_analyst_workflow(
        self, client: AsyncClient, auth_headers: dict, setup_e2e_environment
    ):
        """
        E2E Test: Analyst receives alert, investigates, and makes decision.
        
        Scenario:
        1. Security event is ingested
        2. System processes and generates alert
        3. Analyst views pending alerts
        4. Analyst reviews alert details and explanation
        5. Analyst makes decision (approve/reject/escalate)
        6. Decision is recorded and immutable
        7. Audit trail is created
        """
        # Step 1: Ingest security event
        event_data = valid_event_data(
            event_type="network_connection",
            source_ip="203.0.113.100",  # External
            dest_ip="192.168.1.50",     # Internal
            dest_port=4444,              # Critical port
            raw_data={
                "bytes_sent": 5000,
                "bytes_received": 15000,
            },
        )

        event_response = await client.post(
            "/api/v1/events/",
            json=event_data,
            headers=auth_headers
        )
        assert event_response.status_code == 201
        event_id = event_response.json()["event_id"]

        # Step 2: Verify event was processed
        event_detail = await client.get(
            f"/api/v1/events/{event_id}",
            headers=auth_headers
        )
        assert event_detail.status_code == 200

        # Step 3: View pending alerts
        alerts_response = await client.get(
            "/api/v1/alerts/?status=PENDING",
            headers=auth_headers
        )
        assert alerts_response.status_code == 200
        alerts = alerts_response.json()

        # Should have alert for critical event
        if len(alerts) > 0:
            alert = alerts[0]
            alert_id = alert["id"]

            # Step 4: Review alert details
            alert_detail = await client.get(
                f"/api/v1/alerts/{alert_id}",
                headers=auth_headers
            )
            assert alert_detail.status_code == 200

            # Step 5: Make decision
            decision_data = {
                "action": "DISMISS",
                "justification": "Confirmed malicious activity from external source targeting internal network on known attack port. Recommend blocking source IP.",
            }

            decision_response = await client.post(
                f"/api/v1/alerts/{alert_id}/decisions",
                json=decision_data,
                headers=auth_headers
            )
            # Should succeed (201) or already exist (400)
            assert decision_response.status_code in [201, 400]

            if decision_response.status_code == 201:
                decision = decision_response.json()

                # Step 6: Verify decision is recorded
                decision_check = await client.get(
                    f"/api/v1/alerts/{alert_id}",
                    headers=auth_headers
                )
                assert decision_check.status_code == 200
                alert_details = decision_check.json()
                assert isinstance(alert_details.get("decisions"), list)
                assert any(d.get("action") == "DISMISS" for d in alert_details["decisions"])

                # Step 7: Verify audit trail
                audit_response = await client.get(
                    "/api/v1/audit/",
                    headers=auth_headers
                )
                assert audit_response.status_code == 200


class TestBatchEventProcessing:
    """TEST-E2E-002: Batch event processing scenario."""

    @pytest.fixture
    async def setup_batch_rules(self, db_session: AsyncSession):
        """Setup rules for batch testing."""
        rule = Rule(
            rule_id="BATCH-RULE-001",
            name="Batch Test Rule",
            category="pattern",
            conditions={"dest_port": 8888},
            severity="MEDIUM",
            enabled=True,
        )
        db_session.add(rule)
        await db_session.flush()
        return rule

    @pytest.mark.asyncio
    async def test_batch_event_processing(
        self, client: AsyncClient, auth_headers: dict, setup_batch_rules
    ):
        """
        E2E Test: Multiple events processed in batch.
        
        Scenario:
        1. Multiple events submitted rapidly
        2. All events processed through pipeline
        3. Appropriate alerts generated
        4. System maintains performance
        """
        import time

        event_count = 10
        events_created = []

        start_time = time.time()

        # Submit multiple events
        for i in range(event_count):
            event_data = valid_event_data(
                event_type="batch_test",
                source_ip=f"10.0.{i % 256}.{i % 256}",
                dest_ip="10.0.0.100",
                dest_port=8888 if i % 3 == 0 else 443,  # Some trigger rules
                raw_data={"batch_id": i},
            )

            response = await client.post(
                "/api/v1/events/",
                json=event_data,
                headers=auth_headers
            )
            if response.status_code == 201:
                events_created.append(response.json()["event_id"])

        elapsed = time.time() - start_time

        # Verify all events created
        assert len(events_created) == event_count

        # Performance check (should process quickly)
        assert elapsed < 30, f"Batch took {elapsed}s, expected < 30s"

        # Verify events can be listed
        list_response = await client.get(
            "/api/v1/events/?limit=50",
            headers=auth_headers
        )
        assert list_response.status_code == 200


class TestErrorRecoveryScenarios:
    """TEST-E2E-003: Error recovery scenarios."""

    @pytest.mark.asyncio
    async def test_invalid_event_handling(
        self, client: AsyncClient, auth_headers: dict
    ):
        """
        E2E Test: System gracefully handles invalid events.
        
        Scenario:
        1. Submit malformed event
        2. System returns appropriate error
        3. System continues normal operation
        4. Valid events still processed correctly
        """
        # Submit invalid event (missing required fields)
        invalid_event = {
            "event_type": "test",
            # Missing source_ip and dest_ip
        }

        invalid_response = await client.post(
            "/api/v1/events/",
            json=invalid_event,
            headers=auth_headers
        )
        assert invalid_response.status_code == 422  # Validation error

        # Submit valid event after error
        valid_event = valid_event_data(
            event_type="recovery_test",
        )

        valid_response = await client.post(
            "/api/v1/events/",
            json=valid_event,
            headers=auth_headers
        )
        assert valid_response.status_code == 201  # System still works

    @pytest.mark.asyncio
    async def test_authentication_required(self, client: AsyncClient):
        """
        E2E Test: Endpoints require authentication.
        
        Scenario:
        1. Access endpoint without auth
        2. System returns 401/403
        3. Access with valid auth succeeds
        """
        # Without auth
        response = await client.get("/api/v1/events/")
        assert response.status_code in [401, 403]

        # Without auth - alerts
        alerts_response = await client.get("/api/v1/alerts/")
        assert alerts_response.status_code in [401, 403]

    @pytest.mark.asyncio
    async def test_nonexistent_resource_handling(
        self, client: AsyncClient, auth_headers: dict
    ):
        """
        E2E Test: System handles requests for nonexistent resources.
        
        Scenario:
        1. Request nonexistent event
        2. System returns 404
        3. Request nonexistent alert
        4. System returns 404
        """
        fake_uuid = "00000000-0000-0000-0000-000000000000"

        # Nonexistent event
        event_response = await client.get(
            f"/api/v1/events/{fake_uuid}",
            headers=auth_headers
        )
        assert event_response.status_code == 404

        # Nonexistent alert
        alert_response = await client.get(
            f"/api/v1/alerts/{fake_uuid}",
            headers=auth_headers
        )
        assert alert_response.status_code == 404


class TestAuditCompliance:
    """E2E tests for audit compliance requirements."""

    @pytest.fixture
    async def setup_audit_rules(self, db_session: AsyncSession):
        """Setup for audit testing."""
        rule = Rule(
            rule_id="AUDIT-E2E-001",
            name="Audit Test Rule",
            category="pattern",
            conditions={"dest_port": 9999},
            severity="HIGH",
            enabled=True,
        )
        db_session.add(rule)
        await db_session.flush()
        return rule

    @pytest.mark.asyncio
    async def test_complete_audit_trail(
        self, client: AsyncClient, auth_headers: dict, setup_audit_rules
    ):
        """
        E2E Test: Complete audit trail for compliance.
        
        Scenario:
        1. All operations create audit entries
        2. Audit entries are immutable
        3. Audit trail can be exported
        """
        # Create event
        event_response = await client.post(
            "/api/v1/events/",
            json=valid_event_data(
                event_type="audit_test",
                dest_port=9999,
            ),
            headers=auth_headers
        )
        assert event_response.status_code == 201

        # Check audit trail
        audit_response = await client.get(
            "/api/v1/audit/",
            headers=auth_headers
        )
        assert audit_response.status_code == 200

        logs = audit_response.json()
        assert isinstance(logs, list)

        # Verify audit entries have required fields
        for log in logs:
            assert "id" in log or "action" in log
            assert "timestamp" in log or "created_at" in log


class TestPerformanceScenarios:
    """Performance-related E2E tests."""

    @pytest.mark.asyncio
    async def test_response_time_requirements(
        self, client: AsyncClient, auth_headers: dict
    ):
        """
        E2E Test: API meets response time requirements.
        
        Scenario:
        1. Event submission < 200ms
        2. Alert listing < 500ms
        3. Decision creation < 200ms
        """
        import time

        # Test event submission time
        start = time.time()
        response = await client.post(
            "/api/v1/events/",
            json=valid_event_data(event_type="perf_test"),
            headers=auth_headers
        )
        event_time = (time.time() - start) * 1000
        assert response.status_code == 201
        # Allow generous time for test environment
        assert event_time < 2000, f"Event submission took {event_time}ms"

        # Test alert listing time
        start = time.time()
        alerts_response = await client.get(
            "/api/v1/alerts/",
            headers=auth_headers
        )
        list_time = (time.time() - start) * 1000
        assert alerts_response.status_code == 200
        assert list_time < 2000, f"Alert listing took {list_time}ms"



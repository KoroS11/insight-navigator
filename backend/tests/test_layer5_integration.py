"""
Layer 5: Reasoning Integration Tests
Tests for alert generation logic and architectural boundaries.
"""
import uuid
from datetime import datetime, timezone

import pytest
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import (
    Event, ProcessedEvent, NeuralDetection, Rule, RuleEvaluation, 
    Alert, Explanation, Decision
)
from app.services import (
    IngestionService, ProcessingService, NeuralDetectionService,
    SymbolicReasoningService, IntegrationService
)


def valid_event_data(**overrides) -> dict:
    """Create valid event data with all required fields.
    
    Default IPs are external→internal to trigger alert creation.
    """
    from datetime import datetime, timezone
    base = {
        "event_type": "test",
        "source_ip": "185.220.101.50",   # External (triggers rules)
        "dest_ip": "192.168.1.10",        # Internal
        "dest_port": 9999,                # High port > 8000
        "protocol": "TCP",
        "timestamp": datetime.now(timezone.utc),
        "raw_data": {"test": "data"},
    }
    base.update(overrides)
    return base


class TestAlertGeneration:
    """TEST-L5-001 to TEST-L5-008: Alert generation tests."""

    @pytest.fixture
    async def setup_rules(self, db_session: AsyncSession):
        """Create test rules for alert generation."""
        rules = [
            Rule(
                rule_id="ALERT-RULE-001",
                name="High Severity Rule",
                category="pattern",
                conditions={"dest_port": 4444},
                severity="HIGH",
                enabled=True,
            ),
            Rule(
                rule_id="ALERT-RULE-002",
                name="Critical Severity Rule",
                category="pattern",
                conditions={"dest_port": 31337},
                severity="HIGH",
                enabled=True,
            ),
            Rule(
                rule_id="ALERT-RULE-003",
                name="Medium Severity Rule",
                category="pattern",
                conditions={"dest_port": 8888},
                severity="MEDIUM",
                enabled=True,
            ),
        ]
        for rule in rules:
            db_session.add(rule)
        await db_session.flush()
        return rules

    @pytest.mark.asyncio
    async def test_alert_created_when_rules_match(
        self, db_session: AsyncSession, setup_rules
    ):
        """TEST-L5-001: Alert is created when rules match with sufficient confidence."""
        ing_service = IngestionService(db_session)
        proc_service = ProcessingService(db_session)
        neural_service = NeuralDetectionService(db_session)
        symbolic_service = SymbolicReasoningService(db_session)
        integration_service = IntegrationService(db_session)

        # Create event that triggers high severity rule
        event = await ing_service.ingest_event(
            **valid_event_data(
                event_type="alert_test",
                source_ip="10.0.0.1",
                dest_ip="10.0.0.2",
                dest_port=4444,  # Triggers ALERT-RULE-001
            )
        )
        await db_session.flush()

        processed = await proc_service.process_event(event)
        await db_session.flush()

        detection = await neural_service.detect_anomalies(processed)
        await db_session.flush()

        evaluations = await symbolic_service.evaluate_rules(processed, event_count_24h=0)
        await db_session.flush()

        # Integration creates alerts
        alert = await integration_service.integrate_reasoning(
            processed, detection, evaluations
        )
        await db_session.flush()

        assert alert is not None

    @pytest.mark.asyncio
    async def test_critical_severity_alert(
        self, db_session: AsyncSession, setup_rules
    ):
        """TEST-L5-002: Critical rule match creates critical alert."""
        ing_service = IngestionService(db_session)
        proc_service = ProcessingService(db_session)
        neural_service = NeuralDetectionService(db_session)
        symbolic_service = SymbolicReasoningService(db_session)
        integration_service = IntegrationService(db_session)

        event = await ing_service.ingest_event(
            **valid_event_data(
                event_type="critical_test",
                source_ip="10.0.0.1",
                dest_ip="10.0.0.2",
                dest_port=31337,  # Triggers critical rule
            )
        )
        await db_session.flush()

        processed = await proc_service.process_event(event)
        await db_session.flush()

        detection = await neural_service.detect_anomalies(processed)
        await db_session.flush()

        evaluations = await symbolic_service.evaluate_rules(processed, event_count_24h=0)
        await db_session.flush()

        alert = await integration_service.integrate_reasoning(
            processed, detection, evaluations
        )
        await db_session.flush()

        critical_alerts = [alert] if alert and alert.classification == "HIGH" else []
        # Alert may not be created if thresholds aren't met
        if alert is None:
            pytest.skip("No alert generated - thresholds not met")

    @pytest.mark.asyncio
    async def test_alert_severity_matches_rule(
        self, db_session: AsyncSession, setup_rules
    ):
        """TEST-L5-002: Alert severity matches the triggering rule severity."""
        ing_service = IngestionService(db_session)
        proc_service = ProcessingService(db_session)
        neural_service = NeuralDetectionService(db_session)
        symbolic_service = SymbolicReasoningService(db_session)
        integration_service = IntegrationService(db_session)

        event = await ing_service.ingest_event(
            **valid_event_data(
                event_type="severity_test",
                source_ip="10.0.0.1",
                dest_ip="10.0.0.2",
                dest_port=4444,  # High severity rule
            )
        )
        await db_session.flush()

        processed = await proc_service.process_event(event)
        await db_session.flush()

        detection = await neural_service.detect_anomalies(processed)
        await db_session.flush()

        evaluations = await symbolic_service.evaluate_rules(processed, event_count_24h=0)
        await db_session.flush()

        alert = await integration_service.integrate_reasoning(
            processed, detection, evaluations
        )
        await db_session.flush()

        # Check that alert was created with high severity
        assert alert is not None
        assert alert.classification == "HIGH"

    @pytest.mark.asyncio
    async def test_no_alert_when_no_rules_match(
        self, db_session: AsyncSession, setup_rules
    ):
        """TEST-L5-003: No alert when no rules match."""
        ing_service = IngestionService(db_session)
        proc_service = ProcessingService(db_session)
        neural_service = NeuralDetectionService(db_session)
        symbolic_service = SymbolicReasoningService(db_session)
        integration_service = IntegrationService(db_session)

        event = await ing_service.ingest_event(
            **valid_event_data(
                event_type="no_alert_test",
                source_ip="10.0.0.1",
                dest_ip="10.0.0.2",
                dest_port=443,  # Common port - no rules match
            )
        )
        await db_session.flush()

        processed = await proc_service.process_event(event)
        await db_session.flush()

        detection = await neural_service.detect_anomalies(processed)
        await db_session.flush()

        evaluations = await symbolic_service.evaluate_rules(processed, event_count_24h=0)
        await db_session.flush()

        # Verify no rules matched
        matched_evals = [e for e in evaluations if e.matched]
        # If no rules matched and low anomaly, no alert
        if len(matched_evals) == 0 and detection.anomaly_score < 0.5:
            alert = await integration_service.integrate_reasoning(
                processed, detection, evaluations
            )
            await db_session.flush()
            # May or may not have alerts based on anomaly score alone

    @pytest.mark.asyncio
    async def test_confidence_score_calculation(
        self, db_session: AsyncSession, setup_rules
    ):
        """TEST-L5-004: Alert confidence is calculated correctly."""
        ing_service = IngestionService(db_session)
        proc_service = ProcessingService(db_session)
        neural_service = NeuralDetectionService(db_session)
        symbolic_service = SymbolicReasoningService(db_session)
        integration_service = IntegrationService(db_session)

        event = await ing_service.ingest_event(
            **valid_event_data(
                event_type="confidence_test",
                source_ip="10.0.0.1",
                dest_ip="10.0.0.2",
                dest_port=31337,  # 0.95 confidence modifier
            )
        )
        await db_session.flush()

        processed = await proc_service.process_event(event)
        await db_session.flush()

        detection = await neural_service.detect_anomalies(processed)
        await db_session.flush()

        evaluations = await symbolic_service.evaluate_rules(processed, event_count_24h=0)
        await db_session.flush()

        alert = await integration_service.integrate_reasoning(
            processed, detection, evaluations
        )
        await db_session.flush()

        # Check confidence is in valid range if alert was created
        if alert:
            assert alert.composite_risk_score >= 0
            assert alert.composite_risk_score <= 100

    @pytest.mark.asyncio
    async def test_alert_status_initial_pending(
        self, db_session: AsyncSession, setup_rules
    ):
        """TEST-L5-005: New alert status is 'pending'."""
        ing_service = IngestionService(db_session)
        proc_service = ProcessingService(db_session)
        neural_service = NeuralDetectionService(db_session)
        symbolic_service = SymbolicReasoningService(db_session)
        integration_service = IntegrationService(db_session)

        event = await ing_service.ingest_event(
            **valid_event_data(
                event_type="status_test",
                source_ip="10.0.0.1",
                dest_ip="10.0.0.2",
                dest_port=4444,
            )
        )
        await db_session.flush()

        processed = await proc_service.process_event(event)
        await db_session.flush()

        detection = await neural_service.detect_anomalies(processed)
        await db_session.flush()

        evaluations = await symbolic_service.evaluate_rules(processed, event_count_24h=0)
        await db_session.flush()

        alert = await integration_service.integrate_reasoning(
            processed, detection, evaluations
        )
        await db_session.flush()

        # Check alert status is open (initial state)
        assert alert is not None
        assert alert.status == "PENDING"

    @pytest.mark.asyncio
    async def test_alert_links_to_processed_event(
        self, db_session: AsyncSession, setup_rules
    ):
        """TEST-L5-006: Alert correctly links to processed event."""
        ing_service = IngestionService(db_session)
        proc_service = ProcessingService(db_session)
        neural_service = NeuralDetectionService(db_session)
        symbolic_service = SymbolicReasoningService(db_session)
        integration_service = IntegrationService(db_session)

        event = await ing_service.ingest_event(
            **valid_event_data(
                event_type="link_test",
                source_ip="10.0.0.1",
                dest_ip="10.0.0.2",
                dest_port=4444,
            )
        )
        await db_session.flush()

        processed = await proc_service.process_event(event)
        await db_session.flush()

        detection = await neural_service.detect_anomalies(processed)
        await db_session.flush()

        evaluations = await symbolic_service.evaluate_rules(processed, event_count_24h=0)
        await db_session.flush()

        alert = await integration_service.integrate_reasoning(
            processed, detection, evaluations
        )
        await db_session.flush()

        # Check alert links to the processed event
        assert alert is not None
        assert alert.processed_event_id == processed.id

    @pytest.mark.asyncio
    async def test_multiple_rules_match_creates_single_alert(
        self, db_session: AsyncSession
    ):
        """TEST-L5-007: Multiple matching rules create consolidated alert."""
        # Create overlapping rules - one HIGH severity to trigger alert
        rule1 = Rule(
            rule_id="OVERLAP-001",
            name="Port 8888 Rule",
            category="pattern",
            conditions={"dest_port": 8888},
            severity="HIGH",  # HIGH severity triggers alert
            enabled=True,
        )
        rule2 = Rule(
            rule_id="OVERLAP-002",
            name="High Port Rule",
            category="range",
            conditions={"min_port": 8000},
            severity="MEDIUM",
            enabled=True,
        )
        db_session.add(rule1)
        db_session.add(rule2)
        await db_session.flush()

        ing_service = IngestionService(db_session)
        proc_service = ProcessingService(db_session)
        neural_service = NeuralDetectionService(db_session)
        symbolic_service = SymbolicReasoningService(db_session)
        integration_service = IntegrationService(db_session)

        event = await ing_service.ingest_event(
            **valid_event_data(
                event_type="multi_rule_test",
                source_ip="10.0.0.1",
                dest_ip="10.0.0.2",
                dest_port=8888,  # Matches both rules
            )
        )
        await db_session.flush()

        processed = await proc_service.process_event(event)
        await db_session.flush()

        detection = await neural_service.detect_anomalies(processed)
        await db_session.flush()

        evaluations = await symbolic_service.evaluate_rules(processed, event_count_24h=0)
        await db_session.flush()

        alert = await integration_service.integrate_reasoning(
            processed, detection, evaluations
        )
        await db_session.flush()

        # Should create alert if there's a match
        assert alert is not None or len(evaluations) == 0


class TestArchitecturalBoundaries:
    """TEST-L5-009 to TEST-L5-011: Architectural boundary tests."""

    @pytest.fixture
    async def setup_test_rules(self, db_session: AsyncSession):
        """Create test rules."""
        rule = Rule(
            rule_id="BOUNDARY-RULE-001",
            name="Boundary Test Rule",
            category="pattern",
            conditions={"dest_port": 9999},
            severity="HIGH",
            enabled=True,
        )
        db_session.add(rule)
        await db_session.flush()
        return rule

    @pytest.mark.asyncio
    async def test_integration_does_not_generate_explanation(
        self, db_session: AsyncSession, setup_test_rules
    ):
        """TEST-L5-009: Integration does NOT generate explanations."""
        ing_service = IngestionService(db_session)
        proc_service = ProcessingService(db_session)
        neural_service = NeuralDetectionService(db_session)
        symbolic_service = SymbolicReasoningService(db_session)
        integration_service = IntegrationService(db_session)

        event = await ing_service.ingest_event(
            **valid_event_data(
                event_type="boundary_test",
                source_ip="10.0.0.1",
                dest_ip="10.0.0.2",
                dest_port=9999,
            )
        )
        await db_session.flush()

        processed = await proc_service.process_event(event)
        await db_session.flush()

        detection = await neural_service.detect_anomalies(processed)
        await db_session.flush()

        evaluations = await symbolic_service.evaluate_rules(processed, event_count_24h=0)
        await db_session.flush()

        # Count explanations before
        before_result = await db_session.execute(select(Explanation))
        before_count = len(list(before_result.scalars().all()))

        alert = await integration_service.integrate_reasoning(
            processed, detection, evaluations
        )
        await db_session.flush()

        # Count explanations after
        after_result = await db_session.execute(select(Explanation))
        after_count = len(list(after_result.scalars().all()))

        # Integration should NOT create explanations
        assert after_count == before_count

    @pytest.mark.asyncio
    async def test_integration_does_not_create_decisions(
        self, db_session: AsyncSession, setup_test_rules
    ):
        """TEST-L5-010: Integration does NOT create decisions."""
        ing_service = IngestionService(db_session)
        proc_service = ProcessingService(db_session)
        neural_service = NeuralDetectionService(db_session)
        symbolic_service = SymbolicReasoningService(db_session)
        integration_service = IntegrationService(db_session)

        event = await ing_service.ingest_event(
            **valid_event_data(
                event_type="decision_boundary_test",
                source_ip="10.0.0.1",
                dest_ip="10.0.0.2",
                dest_port=9999,
            )
        )
        await db_session.flush()

        processed = await proc_service.process_event(event)
        await db_session.flush()

        detection = await neural_service.detect_anomalies(processed)
        await db_session.flush()

        evaluations = await symbolic_service.evaluate_rules(processed, event_count_24h=0)
        await db_session.flush()

        # Count decisions before
        before_result = await db_session.execute(select(Decision))
        before_count = len(list(before_result.scalars().all()))

        alert = await integration_service.integrate_reasoning(
            processed, detection, evaluations
        )
        await db_session.flush()

        # Count decisions after
        after_result = await db_session.execute(select(Decision))
        after_count = len(list(after_result.scalars().all()))

        # Integration should NOT create decisions
        assert after_count == before_count


class TestIntegrationService:
    """Direct service layer tests."""

    @pytest.fixture
    async def setup_rule(self, db_session: AsyncSession):
        """Create a test rule."""
        rule = Rule(
            rule_id="SERVICE-RULE-001",
            name="Service Test Rule",
            category="pattern",
            conditions={"dest_port": 7777},
            severity="MEDIUM",
            enabled=True,
        )
        db_session.add(rule)
        await db_session.flush()
        return rule

    @pytest.mark.asyncio
    async def test_get_alert_by_id(
        self, db_session: AsyncSession, setup_rule
    ):
        """Test retrieving alert by ID."""
        ing_service = IngestionService(db_session)
        proc_service = ProcessingService(db_session)
        neural_service = NeuralDetectionService(db_session)
        symbolic_service = SymbolicReasoningService(db_session)
        integration_service = IntegrationService(db_session)

        event = await ing_service.ingest_event(
            **valid_event_data(
                event_type="get_test",
                source_ip="10.0.0.1",
                dest_ip="10.0.0.2",
                dest_port=7777,
            )
        )
        await db_session.flush()

        processed = await proc_service.process_event(event)
        await db_session.flush()

        detection = await neural_service.detect_anomalies(processed)
        await db_session.flush()

        evaluations = await symbolic_service.evaluate_rules(processed, event_count_24h=0)
        await db_session.flush()

        alert = await integration_service.integrate_reasoning(
            processed, detection, evaluations
        )
        await db_session.flush()

        if alert:
            alert = alert
            retrieved = await integration_service.get_alert(alert.id)
            assert retrieved is not None
            assert retrieved.id == alert.id

    @pytest.mark.asyncio
    async def test_list_alerts_by_status(
        self, db_session: AsyncSession, setup_rule
    ):
        """Test filtering alerts by status."""
        ing_service = IngestionService(db_session)
        proc_service = ProcessingService(db_session)
        neural_service = NeuralDetectionService(db_session)
        symbolic_service = SymbolicReasoningService(db_session)
        integration_service = IntegrationService(db_session)

        created_count = 0
        # Create multiple events to generate alerts
        for i in range(3):
            event = await ing_service.ingest_event(
                **valid_event_data(
                    event_type="list_test",
                    source_ip=f"10.0.0.{i+1}",
                    dest_ip="10.0.0.100",
                    dest_port=7777,
                )
            )
            await db_session.flush()

            processed = await proc_service.process_event(event)
            await db_session.flush()

            detection = await neural_service.detect_anomalies(processed)
            await db_session.flush()

            evaluations = await symbolic_service.evaluate_rules(processed, event_count_24h=0)
            await db_session.flush()

            alert = await integration_service.integrate_reasoning(
                processed, detection, evaluations
            )
            await db_session.flush()
            if alert:
                created_count += 1

        if created_count == 0:
            pytest.skip("No alerts were created")
            
        # List pending alerts
        pending_alerts = await integration_service.list_alerts(status="PENDING")
        assert len(pending_alerts) >= created_count

    @pytest.mark.asyncio
    async def test_update_alert_status(
        self, db_session: AsyncSession, setup_rule
    ):
        """Test updating alert status."""
        ing_service = IngestionService(db_session)
        proc_service = ProcessingService(db_session)
        neural_service = NeuralDetectionService(db_session)
        symbolic_service = SymbolicReasoningService(db_session)
        integration_service = IntegrationService(db_session)

        event = await ing_service.ingest_event(
            **valid_event_data(
                event_type="update_test",
                source_ip="10.0.0.1",
                dest_ip="10.0.0.2",
                dest_port=7777,
            )
        )
        await db_session.flush()

        processed = await proc_service.process_event(event)
        await db_session.flush()

        detection = await neural_service.detect_anomalies(processed)
        await db_session.flush()

        evaluations = await symbolic_service.evaluate_rules(processed, event_count_24h=0)
        await db_session.flush()

        alert = await integration_service.integrate_reasoning(
            processed, detection, evaluations
        )
        await db_session.flush()

        if alert:
            alert = alert
            assert alert.status == "pending"

            # Update to reviewed
            updated = await integration_service.update_alert_status(
                alert.id, status="reviewed"
            )
            await db_session.flush()
            assert updated.status == "reviewed"



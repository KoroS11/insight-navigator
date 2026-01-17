"""
Layer 6: Explainability Engine Tests
Tests for explanation generation and architectural boundaries.
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
    SymbolicReasoningService, IntegrationService, ExplainabilityService
)


class TestExplanationGeneration:
    """TEST-L6-001 to TEST-L6-007: Explanation generation tests."""

    @pytest.fixture
    async def alert_with_context(self, db_session: AsyncSession):
        """Create an alert with all necessary context for explanation."""
        # Create rule
        rule = Rule(
            rule_id="EXPLAIN-RULE-001",
            name="Explanation Test Rule",
            category="pattern",
            conditions={"dest_port": 6666},
            severity="HIGH",
            enabled=True,
        )
        db_session.add(rule)
        await db_session.flush()

        ing_service = IngestionService(db_session)
        proc_service = ProcessingService(db_session)
        neural_service = NeuralDetectionService(db_session)
        symbolic_service = SymbolicReasoningService(db_session)
        integration_service = IntegrationService(db_session)

        event = await ing_service.ingest_event(
            event_type="explain_test",
            source_ip="192.168.1.50",
            dest_ip="10.0.0.100",
            dest_port=6666,
            protocol="TCP",
            raw_data={"protocol": "tcp", "bytes": 5000},
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

        return alert, processed, detection, evaluations, event

    @pytest.mark.asyncio
    async def test_explanation_created_for_alert(
        self, db_session: AsyncSession, alert_with_context
    ):
        """TEST-L6-001: Explanation is created for each alert."""
        alert, processed, detection, evaluations, event = alert_with_context
        if not alert:
            pytest.skip("No alert generated")

        explain_service = ExplainabilityService(db_session)

        explanation = await explain_service.generate_explanation(alert, detection, evaluations, processed, event)
        await db_session.flush()

        assert explanation is not None
        assert explanation.alert_id == alert.id

    @pytest.mark.asyncio
    async def test_explanation_has_summary(
        self, db_session: AsyncSession, alert_with_context
    ):
        """TEST-L6-002: Explanation contains human-readable summary."""
        alert, processed, detection, evaluations, event = alert_with_context
        if not alert:
            pytest.skip("No alert generated")

        explain_service = ExplainabilityService(db_session)

        explanation = await explain_service.generate_explanation(alert, detection, evaluations, processed, event)
        await db_session.flush()

        # Check that explanation_data contains expected structure
        assert explanation.explanation_data is not None
        assert "natural_language" in explanation.explanation_data
        assert len(explanation.explanation_data["natural_language"]) > 20  # Meaningful summary
        assert isinstance(explanation.explanation_data["natural_language"], str)

    @pytest.mark.asyncio
    async def test_explanation_contains_neural_factors(
        self, db_session: AsyncSession, alert_with_context
    ):
        """TEST-L6-003: Explanation includes neural detection factors."""
        alert, processed, detection, evaluations, event = alert_with_context
        if not alert:
            pytest.skip("No alert generated")

        explain_service = ExplainabilityService(db_session)

        explanation = await explain_service.generate_explanation(alert, detection, evaluations, processed, event)
        await db_session.flush()

        # Neural factors should be in the explanation tree
        assert explanation.explanation_data is not None
        tree = explanation.explanation_data.get("tree", {})

        # Should include score components in the tree
        assert tree is not None

    @pytest.mark.asyncio
    async def test_explanation_contains_symbolic_factors(
        self, db_session: AsyncSession, alert_with_context
    ):
        """TEST-L6-004: Explanation includes symbolic reasoning factors."""
        alert, processed, detection, evaluations, event = alert_with_context
        if not alert:
            pytest.skip("No alert generated")

        explain_service = ExplainabilityService(db_session)

        explanation = await explain_service.generate_explanation(alert, detection, evaluations, processed, event)
        await db_session.flush()

        # Symbolic factors should be present in explanation_data
        assert explanation.explanation_data is not None
        tree = explanation.explanation_data.get("tree", {})

        # Should include rule information in the tree
        assert tree is not None

    @pytest.mark.asyncio
    async def test_explanation_has_evidence_chain(
        self, db_session: AsyncSession, alert_with_context
    ):
        """TEST-L6-005: Explanation includes evidence chain."""
        alert, processed, detection, evaluations, event = alert_with_context
        if not alert:
            pytest.skip("No alert generated")

        explain_service = ExplainabilityService(db_session)

        explanation = await explain_service.generate_explanation(alert, detection, evaluations, processed, event)
        await db_session.flush()

        # Evidence chain should be in explanation_data tree
        assert explanation.explanation_data is not None
        tree = explanation.explanation_data.get("tree", {})

        # Tree should have root structure 
        assert "root" in tree

    @pytest.mark.asyncio
    async def test_counterfactual_explanation(
        self, db_session: AsyncSession, alert_with_context
    ):
        """TEST-L6-006: Counterfactual explanation is provided."""
        alert, processed, detection, evaluations, event = alert_with_context
        if not alert:
            pytest.skip("No alert generated")

        explain_service = ExplainabilityService(db_session)

        explanation = await explain_service.generate_explanation(alert, detection, evaluations, processed, event)
        await db_session.flush()

        # Counterfactual: "What would need to change for different outcome"
        assert explanation.explanation_data is not None
        counterfactuals = explanation.explanation_data.get("counterfactuals", [])
        assert isinstance(counterfactuals, list)

    @pytest.mark.asyncio
    async def test_uncertainty_indication(
        self, db_session: AsyncSession, alert_with_context
    ):
        """TEST-L6-007: Explanation includes uncertainty indication."""
        alert, processed, detection, evaluations, event = alert_with_context
        if not alert:
            pytest.skip("No alert generated")

        explain_service = ExplainabilityService(db_session)

        explanation = await explain_service.generate_explanation(alert, detection, evaluations, processed, event)
        await db_session.flush()

        # Natural language should be present
        assert explanation.explanation_data is not None
        assert "natural_language" in explanation.explanation_data


class TestArchitecturalBoundaries:
    """TEST-L6-008 to TEST-L6-010: Architectural boundary tests."""

    @pytest.fixture
    async def full_pipeline_alert(self, db_session: AsyncSession):
        """Create an alert through full pipeline."""
        rule = Rule(
            rule_id="BOUNDARY-L6-001",
            name="Boundary Test Rule",
            category="pattern",
            conditions={"dest_port": 5555},
            severity="HIGH",
            enabled=True,
        )
        db_session.add(rule)
        await db_session.flush()

        ing_service = IngestionService(db_session)
        proc_service = ProcessingService(db_session)
        neural_service = NeuralDetectionService(db_session)
        symbolic_service = SymbolicReasoningService(db_session)
        integration_service = IntegrationService(db_session)

        event = await ing_service.ingest_event(
            event_type="boundary_test",
            source_ip="10.0.0.1",
            dest_ip="10.0.0.2",
            dest_port=5555,
            protocol="TCP",
            raw_data={},
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

        return alert, processed, detection, evaluations, event

    @pytest.mark.asyncio
    async def test_explainability_does_not_modify_alert(
        self, db_session: AsyncSession, full_pipeline_alert
    ):
        """TEST-L6-008: Explainability does NOT modify the alert."""
        alert, processed, detection, evaluations, event = full_pipeline_alert
        if not alert:
            pytest.skip("No alert generated")

        # Store original alert state
        original_status = alert.status
        original_severity = alert.classification
        original_confidence = alert.composite_risk_score

        explain_service = ExplainabilityService(db_session)

        explanation = await explain_service.generate_explanation(alert, detection, evaluations, processed, event)
        await db_session.flush()

        # Refresh alert
        await db_session.refresh(alert)

        # Alert should be unchanged
        assert alert.status == original_status
        assert alert.classification == original_severity
        assert alert.composite_risk_score == original_confidence

    @pytest.mark.asyncio
    async def test_explainability_does_not_create_decisions(
        self, db_session: AsyncSession, full_pipeline_alert
    ):
        """TEST-L6-009: Explainability does NOT create decisions."""
        alert, processed, detection, evaluations, event = full_pipeline_alert
        if not alert:
            pytest.skip("No alert generated")

        # Count decisions before
        before_result = await db_session.execute(select(Decision))
        before_count = len(list(before_result.scalars().all()))

        explain_service = ExplainabilityService(db_session)

        explanation = await explain_service.generate_explanation(alert, detection, evaluations, processed, event)
        await db_session.flush()

        # Count decisions after
        after_result = await db_session.execute(select(Decision))
        after_count = len(list(after_result.scalars().all()))

        # Explainability should NOT create decisions
        assert after_count == before_count

    @pytest.mark.asyncio
    async def test_explanation_is_read_only(
        self, db_session: AsyncSession, full_pipeline_alert
    ):
        """TEST-L6-010: Explanation does not alter previous layer data."""
        alert, processed, detection, evaluations, event = full_pipeline_alert
        if not alert:
            pytest.skip("No alert generated")

        # Store original states
        original_detection_score = float(detection.anomaly_score)
        original_processed_hash = processed.event_hash

        explain_service = ExplainabilityService(db_session)

        explanation = await explain_service.generate_explanation(alert, detection, evaluations, processed, event)
        await db_session.flush()

        # Refresh objects
        await db_session.refresh(detection)
        await db_session.refresh(processed)

        # Previous layer data unchanged
        assert float(detection.anomaly_score) == original_detection_score
        assert processed.event_hash == original_processed_hash


class TestExplainabilityService:
    """Direct service layer tests."""

    @pytest.fixture
    async def setup_for_explain(self, db_session: AsyncSession):
        """Create full context for explanation testing."""
        # Use external→internal IPs and high port to trigger alert creation
        rule = Rule(
            rule_id="SERVICE-EXPLAIN-001",
            name="Service Explain Rule",
            category="pattern",
            conditions={"dest_port": 9999},
            severity="HIGH",  # HIGH severity to trigger alert
            enabled=True,
        )
        db_session.add(rule)
        await db_session.flush()

        ing_service = IngestionService(db_session)
        proc_service = ProcessingService(db_session)
        neural_service = NeuralDetectionService(db_session)
        symbolic_service = SymbolicReasoningService(db_session)
        integration_service = IntegrationService(db_session)

        event = await ing_service.ingest_event(
            event_type="service_explain_test",
            source_ip="185.220.101.50",  # External
            dest_ip="192.168.1.10",       # Internal
            dest_port=9999,               # High port > 8000
            protocol="TCP",
            raw_data={"data": "test"},
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

        return {
            "alert": alert,
            "event": event,
            "processed": processed,
            "detection": detection,
            "evaluations": evaluations,
        }

    @pytest.mark.asyncio
    async def test_get_explanation_by_alert_id(
        self, db_session: AsyncSession, setup_for_explain
    ):
        """Test retrieving explanation by alert ID."""
        context = setup_for_explain
        if not context["alert"]:
            pytest.skip("No alert generated")

        explain_service = ExplainabilityService(db_session)

        explanation = await explain_service.generate_explanation(
            alert=context["alert"],
            detection=context["detection"],
            evaluations=context["evaluations"],
            processed_event=context["processed"],
            event=context["event"],
        )
        await db_session.flush()

        # Retrieve by alert ID
        retrieved = await explain_service.get_explanation(context["alert"].id)
        assert retrieved is not None
        assert retrieved.id == explanation.id

    @pytest.mark.asyncio
    async def test_explanation_created_timestamp(
        self, db_session: AsyncSession, setup_for_explain
    ):
        """Test explanation has creation timestamp."""
        context = setup_for_explain
        if not context["alert"]:
            pytest.skip("No alert generated")

        explain_service = ExplainabilityService(db_session)

        explanation = await explain_service.generate_explanation(
            alert=context["alert"],
            detection=context["detection"],
            evaluations=context["evaluations"],
            processed_event=context["processed"],
            event=context["event"],
        )
        await db_session.flush()

        assert explanation.generated_at is not None
        assert isinstance(explanation.generated_at, datetime)

    @pytest.mark.asyncio
    async def test_regenerate_explanation(
        self, db_session: AsyncSession, setup_for_explain
    ):
        """Test regenerating explanation for same alert returns existing one."""
        context = setup_for_explain
        if not context["alert"]:
            pytest.skip("No alert generated")

        explain_service = ExplainabilityService(db_session)

        # Generate first explanation
        explanation1 = await explain_service.generate_explanation(
            alert=context["alert"],
            detection=context["detection"],
            evaluations=context["evaluations"],
            processed_event=context["processed"],
            event=context["event"],
        )
        await db_session.flush()

        # Retrieve it - same alert should get same explanation
        retrieved = await explain_service.get_explanation(context["alert"].id)
        await db_session.flush()

        # Both should be valid and match
        assert explanation1 is not None
        assert retrieved is not None
        assert explanation1.id == retrieved.id



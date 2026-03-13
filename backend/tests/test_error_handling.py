"""
Error Handling Tests
Tests for graceful error handling and recovery.
"""
import uuid
from datetime import datetime, timezone

import pytest
from httpx import AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Event, Rule


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


class TestValidationErrors:
    """ERR-001: Validation error handling tests."""

    @pytest.mark.asyncio
    async def test_missing_required_field_error_format(
        self, client: AsyncClient, auth_headers: dict
    ):
        """ERR-001 Case 1: Missing field returns proper error format."""
        response = await client.post(
            "/api/v1/events/",
            json={
                "event_type": "test",
                # Missing source_ip and dest_ip
            },
            headers=auth_headers
        )

        assert response.status_code == 422
        error = response.json()
        
        # Should have detail field with validation errors
        assert "detail" in error
        # Detail should explain what's missing

    @pytest.mark.asyncio
    async def test_invalid_type_error_format(
        self, client: AsyncClient, auth_headers: dict
    ):
        """ERR-001 Case 2: Invalid type returns proper error."""
        event_data = valid_event_data(dest_port="not_a_number")  # Should be int

        response = await client.post(
            "/api/v1/events/",
            json=event_data,
            headers=auth_headers
        )

        assert response.status_code == 422
        error = response.json()
        assert "detail" in error

    @pytest.mark.asyncio
    async def test_invalid_uuid_format(
        self, client: AsyncClient, auth_headers: dict
    ):
        """ERR-001 Case 3: Invalid UUID returns 400/404."""
        response = await client.get(
            "/api/v1/events/not-a-valid-uuid",
            headers=auth_headers
        )

        assert response.status_code in [400, 404, 422]

    @pytest.mark.asyncio
    async def test_constraint_violation_error(
        self, client: AsyncClient, auth_headers: dict
    ):
        """ERR-001 Case 4: Constraint violation returns proper error."""
        event_data = valid_event_data(dest_port=99999)  # Port > 65535

        response = await client.post(
            "/api/v1/events/",
            json=event_data,
            headers=auth_headers
        )

        assert response.status_code in [400, 422]


class TestNotFoundErrors:
    """ERR-002: Not found error handling tests."""

    @pytest.mark.asyncio
    async def test_event_not_found(
        self, client: AsyncClient, auth_headers: dict
    ):
        """ERR-002 Case 1: Nonexistent event returns 404."""
        fake_uuid = str(uuid.uuid4())
        
        response = await client.get(
            f"/api/v1/events/{fake_uuid}",
            headers=auth_headers
        )

        assert response.status_code == 404
        error = response.json()
        assert "detail" in error or "message" in error

    @pytest.mark.asyncio
    async def test_alert_not_found(
        self, client: AsyncClient, auth_headers: dict
    ):
        """ERR-002 Case 2: Nonexistent alert returns 404."""
        fake_uuid = str(uuid.uuid4())
        
        response = await client.get(
            f"/api/v1/alerts/{fake_uuid}",
            headers=auth_headers
        )

        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_decision_for_nonexistent_alert(
        self, client: AsyncClient, auth_headers: dict
    ):
        """ERR-002 Case 3: Decision for nonexistent alert returns 404 (not found)."""
        fake_uuid = str(uuid.uuid4())
        
        response = await client.post(
            f"/api/v1/alerts/{fake_uuid}/decisions",
            json={
                "action": "ESCALATE",
                "justification": "Test reasoning for nonexistent alert.",
            },
            headers=auth_headers
        )

        # Router returns 404 for nonexistent alert
        assert response.status_code == 404


class TestAuthenticationErrors:
    """Authentication error handling tests."""

    @pytest.mark.asyncio
    async def test_no_token_error_message(self, client: AsyncClient):
        """Missing token returns clear error."""
        response = await client.get("/api/v1/events/")
        
        assert response.status_code in [401, 403]
        # Should have informative error message

    @pytest.mark.asyncio
    async def test_invalid_token_error_message(self, client: AsyncClient):
        """Invalid token returns clear error."""
        response = await client.get(
            "/api/v1/events/",
            headers={"Authorization": "Bearer invalid_token"}
        )
        
        assert response.status_code in [401, 403]

    @pytest.mark.asyncio
    async def test_expired_token_error_message(self, client: AsyncClient):
        """Expired token returns specific error."""
        from app.core.security import create_access_token
        from datetime import timedelta
        
        expired_token = create_access_token(
            username="expired_test_user",
            expires_delta=timedelta(seconds=-10)
        )
        
        response = await client.get(
            "/api/v1/events/",
            headers={"Authorization": f"Bearer {expired_token}"}
        )
        
        assert response.status_code in [401, 403]


class TestDatabaseErrors:
    """Database error handling tests."""

    @pytest.mark.asyncio
    async def test_duplicate_handling(
        self, db_session: AsyncSession, client: AsyncClient, auth_headers: dict
    ):
        """Duplicate entries are handled gracefully."""
        # Create two identical events (should be allowed - events aren't unique)
        event_data = valid_event_data(event_type="duplicate_test")

        response1 = await client.post(
            "/api/v1/events/",
            json=event_data,
            headers=auth_headers
        )
        assert response1.status_code == 201

        response2 = await client.post(
            "/api/v1/events/",
            json=event_data,
            headers=auth_headers
        )
        assert response2.status_code == 201

        # Both should succeed (events are not unique constrained)


class TestServiceErrors:
    """Service layer error handling tests."""

    @pytest.mark.asyncio
    async def test_invalid_decision_action(
        self, client: AsyncClient, auth_headers: dict, db_session: AsyncSession
    ):
        """Invalid decision action returns validation error."""
        # Create a rule and event to get an alert
        rule = Rule(
            rule_id="ERR-DECISION-001",
            name="Error Test Rule",
            category="pattern",
            conditions={"dest_port": 7777},
            severity="HIGH",
            enabled=True,
        )
        db_session.add(rule)
        await db_session.flush()

        # Create event
        event_response = await client.post(
            "/api/v1/events/",
            json=valid_event_data(
                event_type="decision_error_test",
                dest_port=7777,
            ),
            headers=auth_headers
        )

        # Get alerts
        alerts_response = await client.get(
            "/api/v1/alerts/",
            headers=auth_headers
        )

        if alerts_response.status_code == 200 and alerts_response.json():
            alert_id = alerts_response.json()[0]["id"]

            # Try invalid action
            response = await client.post(
                f"/api/v1/alerts/{alert_id}/decisions",
                json={
                    "action": "invalid_action",
                    "justification": "Test reasoning for invalid action.",
                },
                headers=auth_headers
            )

            assert response.status_code in [400, 422]
        else:
            # No alert was created, skip the test
            pytest.skip("No alert was created for this test")

    @pytest.mark.asyncio
    async def test_confidence_out_of_range(
        self, client: AsyncClient, auth_headers: dict, db_session: AsyncSession
    ):
        """Confidence outside 0-1 range returns error."""
        rule = Rule(
            rule_id="ERR-CONF-001",
            name="Confidence Error Test Rule",
            category="pattern",
            conditions={"dest_port": 6666},
            severity="HIGH",
            enabled=True,
        )
        db_session.add(rule)
        await db_session.flush()

        event_response = await client.post(
            "/api/v1/events/",
            json=valid_event_data(
                event_type="confidence_error_test",
                dest_port=6666,
            ),
            headers=auth_headers
        )

        alerts_response = await client.get(
            "/api/v1/alerts/",
            headers=auth_headers
        )

        if alerts_response.status_code == 200 and alerts_response.json():
            alert_id = alerts_response.json()[0]["id"]

            # Try confidence > 1
            response = await client.post(
                f"/api/v1/alerts/{alert_id}/decisions",
                json={
                    "action": "DISMISS",
                    "justification": "Test confidence bounds validation.",
                    "confidence": 1.5,  # Invalid
                },
                headers=auth_headers
            )

            assert response.status_code in [400, 422]


class TestMalformedRequests:
    """Malformed request handling tests."""

    @pytest.mark.asyncio
    async def test_invalid_json(
        self, client: AsyncClient, auth_headers: dict
    ):
        """Invalid JSON body returns appropriate error."""
        response = await client.post(
            "/api/v1/events/",
            content="not valid json",
            headers={**auth_headers, "Content-Type": "application/json"}
        )

        assert response.status_code in [400, 422]

    @pytest.mark.asyncio
    async def test_empty_body(
        self, client: AsyncClient, auth_headers: dict
    ):
        """Empty request body returns appropriate error."""
        response = await client.post(
            "/api/v1/events/",
            content="",
            headers={**auth_headers, "Content-Type": "application/json"}
        )

        assert response.status_code in [400, 422]

    @pytest.mark.asyncio
    async def test_wrong_content_type(
        self, client: AsyncClient, auth_headers: dict
    ):
        """Wrong content type is handled gracefully."""
        response = await client.post(
            "/api/v1/events/",
            content="event_type=test",
            headers={**auth_headers, "Content-Type": "text/plain"}
        )

        # Should reject or handle appropriately
        assert response.status_code in [400, 415, 422]


class TestErrorRecovery:
    """Error recovery tests."""

    @pytest.mark.asyncio
    async def test_system_continues_after_error(
        self, client: AsyncClient, auth_headers: dict
    ):
        """System continues to function after error."""
        # Cause an error
        await client.post(
            "/api/v1/events/",
            json={"invalid": "data"},
            headers=auth_headers
        )

        # System should still work
        response = await client.post(
            "/api/v1/events/",
            json=valid_event_data(event_type="recovery_test"),
            headers=auth_headers
        )

        assert response.status_code == 201

    @pytest.mark.asyncio
    async def test_multiple_errors_dont_cascade(
        self, client: AsyncClient, auth_headers: dict
    ):
        """Multiple errors don't cause cascading failures."""
        # Cause multiple errors
        for i in range(5):
            await client.post(
                "/api/v1/events/",
                json={"broken": i},
                headers=auth_headers
            )

        # System should still work
        response = await client.get("/api/v1/events/", headers=auth_headers)
        assert response.status_code == 200



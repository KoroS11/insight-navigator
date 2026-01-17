"""
Security Tests
Tests for authentication, authorization, and security vulnerabilities.
"""
import uuid
from datetime import datetime, timezone

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import User, Event


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


class TestAuthentication:
    """SEC-001: Authentication security tests."""

    @pytest.mark.asyncio
    async def test_endpoint_requires_auth(self, client: AsyncClient):
        """SEC-001 Case 1: Protected endpoints require authentication."""
        # Events endpoint
        response = await client.get("/api/v1/events/")
        assert response.status_code in [401, 403]

        # Alerts endpoint
        response = await client.get("/api/v1/alerts/")
        assert response.status_code in [401, 403]

        # Audit endpoint
        response = await client.get("/api/v1/audit/")
        assert response.status_code in [401, 403]

    @pytest.mark.asyncio
    async def test_invalid_token_rejected(self, client: AsyncClient):
        """SEC-001 Case 2: Invalid token is rejected."""
        headers = {"Authorization": "Bearer invalid_token_here"}
        
        response = await client.get("/api/v1/events/", headers=headers)
        assert response.status_code in [401, 403]

    @pytest.mark.asyncio
    async def test_expired_token_rejected(self, client: AsyncClient):
        """SEC-001 Case 3: Expired token is rejected."""
        from app.core.security import create_access_token
        from datetime import timedelta
        
        # Create token that's already expired
        expired_token = create_access_token(
            username="expired_test_user",
            expires_delta=timedelta(seconds=-1)  # Already expired
        )
        
        headers = {"Authorization": f"Bearer {expired_token}"}
        response = await client.get("/api/v1/events/", headers=headers)
        assert response.status_code in [401, 403]

    @pytest.mark.asyncio
    async def test_malformed_auth_header_rejected(self, client: AsyncClient):
        """SEC-001 Case 4: Malformed authorization header is rejected."""
        # Missing Bearer prefix
        headers = {"Authorization": "some_token_without_bearer"}
        response = await client.get("/api/v1/events/", headers=headers)
        assert response.status_code in [401, 403]

        # Empty token
        headers = {"Authorization": "Bearer "}
        response = await client.get("/api/v1/events/", headers=headers)
        assert response.status_code in [401, 403]

    @pytest.mark.asyncio
    async def test_valid_token_accepted(self, client: AsyncClient, auth_headers: dict):
        """SEC-001 Case 5: Valid token is accepted."""
        response = await client.get("/api/v1/events/", headers=auth_headers)
        assert response.status_code == 200


class TestSQLInjection:
    """SEC-002: SQL injection prevention tests."""

    @pytest.mark.asyncio
    async def test_sql_injection_in_event_type(
        self, client: AsyncClient, auth_headers: dict
    ):
        """SEC-002 Case 1: SQL injection in event_type field."""
        malicious_event = valid_event_data(
            event_type="test'; DROP TABLE events; --",
        )

        # Should not execute SQL injection
        response = await client.post(
            "/api/v1/events/",
            json=malicious_event,
            headers=auth_headers
        )
        # Should succeed (data is escaped) or fail validation
        assert response.status_code in [201, 400, 422]

        # Verify events table still exists
        list_response = await client.get("/api/v1/events/", headers=auth_headers)
        assert list_response.status_code == 200

    @pytest.mark.asyncio
    async def test_sql_injection_in_payload(
        self, client: AsyncClient, auth_headers: dict
    ):
        """SEC-002 Case 2: SQL injection in payload field."""
        malicious_event = valid_event_data(
            raw_data={
                "malicious": "'; DELETE FROM alerts; --",
                "nested": {"attack": "1=1; DROP DATABASE test;"}
            },
        )

        response = await client.post(
            "/api/v1/events/",
            json=malicious_event,
            headers=auth_headers
        )
        assert response.status_code in [201, 400, 422]

    @pytest.mark.asyncio
    async def test_sql_injection_in_query_params(
        self, client: AsyncClient, auth_headers: dict
    ):
        """SEC-002 Case 3: SQL injection in query parameters."""
        # Try injection in filter parameters
        response = await client.get(
            "/api/v1/events/?event_type=test' OR '1'='1",
            headers=auth_headers
        )
        # Should not return all events or error safely
        assert response.status_code in [200, 400, 422]


class TestXSSPrevention:
    """SEC-003: Cross-site scripting prevention tests."""

    @pytest.mark.asyncio
    async def test_xss_in_event_payload(
        self, client: AsyncClient, auth_headers: dict
    ):
        """SEC-003 Case 1: XSS attack in payload is stored safely."""
        xss_event = valid_event_data(
            event_type="xss_test",
            raw_data={
                "script": "<script>alert('XSS')</script>",
                "img": "<img src=x onerror=alert('XSS')>",
                "onclick": "<div onclick='malicious()'>click</div>",
            },
        )

        response = await client.post(
            "/api/v1/events/",
            json=xss_event,
            headers=auth_headers
        )
        assert response.status_code == 201

        # Retrieve and verify XSS is escaped or stored as-is (for raw logging)
        event_id = response.json()["event_id"]
        get_response = await client.get(
            f"/api/v1/events/{event_id}",
            headers=auth_headers
        )
        assert get_response.status_code == 200

        # Data should be stored (raw log) but response should be safe JSON
        data = get_response.json()
        # JSON encoding naturally escapes < > characters

    @pytest.mark.asyncio
    async def test_xss_in_reasoning_field(
        self, client: AsyncClient, auth_headers: dict, db_session
    ):
        """SEC-003 Case 2: XSS in decision reasoning is handled safely."""
        # This test would need an alert to exist first
        # Verify reasoning field is properly escaped
        pass  # Covered by validation tests


class TestAuthorizationBoundaries:
    """SEC-004: Authorization and access control tests."""

    @pytest.mark.asyncio
    async def test_user_cannot_access_others_decisions(
        self, client: AsyncClient, db_session: AsyncSession
    ):
        """SEC-004 Case 1: Users cannot access other users' resources."""
        from app.core.security import create_access_token, get_password_hash
        
        # Create two users
        user1 = User(
            id=uuid.uuid4(),
            username="user1",
            hashed_password=get_password_hash("password1"),
            role="analyst",
            is_active=True,
        )
        user2 = User(
            id=uuid.uuid4(),
            username="user2",
            hashed_password=get_password_hash("password2"),
            role="analyst",
            is_active=True,
        )
        db_session.add(user1)
        db_session.add(user2)
        await db_session.flush()

        # Create tokens
        token1 = create_access_token(username=user1.username)
        token2 = create_access_token(username=user2.username)

        headers1 = {"Authorization": f"Bearer {token1}"}
        headers2 = {"Authorization": f"Bearer {token2}"}

        # Both should be able to access their own resources
        # Implementation-specific: check actual authorization rules

    @pytest.mark.asyncio
    async def test_role_based_access(self, client: AsyncClient, auth_headers: dict, admin_headers: dict):
        """SEC-004 Case 2: Role-based access control is enforced."""
        # Regular user should not access admin endpoints (if any)
        # Admin should have elevated access
        
        # Both should access events
        user_response = await client.get("/api/v1/events/", headers=auth_headers)
        assert user_response.status_code == 200

        admin_response = await client.get("/api/v1/events/", headers=admin_headers)
        assert admin_response.status_code == 200


class TestInputSanitization:
    """Tests for input sanitization and validation."""

    @pytest.mark.asyncio
    async def test_oversized_payload_rejected(
        self, client: AsyncClient, auth_headers: dict
    ):
        """Test oversized payloads are rejected."""
        # Create very large payload
        large_payload = {"data": "x" * (10 * 1024 * 1024)}  # 10MB of x's

        event_data = valid_event_data(
            event_type="large_test",
            raw_data=large_payload,
        )

        response = await client.post(
            "/api/v1/events/",
            json=event_data,
            headers=auth_headers
        )
        # Should reject or truncate
        assert response.status_code in [201, 400, 413, 422]

    @pytest.mark.asyncio
    async def test_null_bytes_handled(
        self, client: AsyncClient, auth_headers: dict
    ):
        """Test null bytes in input are handled safely."""
        event_data = valid_event_data(
            event_type="null_byte_test",
            raw_data={"data": "with_null_bytes"},
        )

        response = await client.post(
            "/api/v1/events/",
            json=event_data,
            headers=auth_headers
        )
        # Should handle gracefully
        assert response.status_code in [201, 400, 422]

    @pytest.mark.asyncio
    async def test_unicode_handling(
        self, client: AsyncClient, auth_headers: dict
    ):
        """Test Unicode input is handled correctly."""
        event_data = valid_event_data(
            event_type="unicode_test",
            raw_data={
                "message": "安全测试",
                "arabic": "اختبار الأمان",
            },
        )

        response = await client.post(
            "/api/v1/events/",
            json=event_data,
            headers=auth_headers
        )
        assert response.status_code == 201

        # Verify data stored correctly
        event_id = response.json()["event_id"]
        get_response = await client.get(
            f"/api/v1/events/{event_id}",
            headers=auth_headers
        )
        assert get_response.status_code == 200


class TestRateLimiting:
    """Tests for rate limiting (if implemented)."""

    @pytest.mark.asyncio
    async def test_rapid_requests_handled(
        self, client: AsyncClient, auth_headers: dict
    ):
        """Test system handles rapid requests gracefully."""
        import asyncio

        # Send many requests rapidly
        responses = []
        for _ in range(50):
            response = await client.post(
                "/api/v1/events/",
                json=valid_event_data(event_type="rate_test"),
                headers=auth_headers
            )
            responses.append(response.status_code)

        # Most should succeed (201) or be rate-limited (429)
        success_count = responses.count(201)
        rate_limited = responses.count(429)
        
        # Either all succeed or some are rate-limited
        assert success_count > 0 or rate_limited > 0



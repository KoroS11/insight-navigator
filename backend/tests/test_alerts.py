"""
Tests for Alerts and Decisions (Layer 5, 6, 7)
"""
import pytest
from datetime import datetime, timezone
from httpx import AsyncClient


async def create_alert(client: AsyncClient, auth_headers: dict) -> str:
    """Helper to create an event that generates an alert."""
    response = await client.post(
        "/api/v1/events/",
        json={
            "event_type": "suspicious_auth",
            "source_ip": "185.220.101.50",  # External
            "dest_ip": "192.168.1.10",       # Internal
            "dest_port": 9999,               # High port > 8000
            "protocol": "TCP",               # Required
            "timestamp": datetime.now(timezone.utc).isoformat(),  # Required
            "raw_data": {"method": "brute_force"},  # Correct field name
        },
        headers=auth_headers,
    )
    return response.json().get("alert_id")


@pytest.mark.asyncio
async def test_list_alerts(client: AsyncClient, auth_headers):
    """Test listing alerts."""
    # Create an alert
    await create_alert(client, auth_headers)
    
    response = await client.get("/api/v1/alerts/", headers=auth_headers)
    
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)


@pytest.mark.asyncio
async def test_get_alert(client: AsyncClient, auth_headers):
    """Test getting a specific alert with full context."""
    alert_id = await create_alert(client, auth_headers)
    
    if alert_id is None:
        pytest.skip("No alert was created")
    
    response = await client.get(f"/api/v1/alerts/{alert_id}", headers=auth_headers)
    
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == alert_id
    assert "composite_risk_score" in data
    assert "classification" in data
    assert "status" in data
    assert "explanation" in data
    assert "decisions" in data


@pytest.mark.asyncio
async def test_get_alert_explanation(client: AsyncClient, auth_headers):
    """Test getting alert explanation."""
    alert_id = await create_alert(client, auth_headers)
    
    if alert_id is None:
        pytest.skip("No alert was created")
    
    response = await client.get(
        f"/api/v1/alerts/{alert_id}/explanation",
        headers=auth_headers,
    )
    
    assert response.status_code == 200
    data = response.json()
    # Response contains explanation_data with tree, natural_language, counterfactuals
    assert "explanation_data" in data
    explanation = data["explanation_data"]
    assert "tree" in explanation
    assert "natural_language" in explanation
    assert "counterfactuals" in explanation
    
    # Verify natural language is human-readable
    assert len(explanation["natural_language"]) > 50


@pytest.mark.asyncio
async def test_update_alert_status(client: AsyncClient, auth_headers):
    """Test updating alert status."""
    alert_id = await create_alert(client, auth_headers)
    
    if alert_id is None:
        pytest.skip("No alert was created")
    
    response = await client.patch(
        f"/api/v1/alerts/{alert_id}/status",
        json={"status": "ESCALATED"},  # Must be uppercase
        headers=auth_headers,
    )
    
    assert response.status_code == 200
    assert response.json()["status"] == "ESCALATED"


@pytest.mark.asyncio
async def test_create_decision(client: AsyncClient, auth_headers):
    """Test creating an analyst decision (Layer 7)."""
    alert_id = await create_alert(client, auth_headers)
    
    if alert_id is None:
        pytest.skip("No alert was created")
    
    response = await client.post(
        f"/api/v1/alerts/{alert_id}/decisions",
        json={
            "action": "ESCALATE",
            "justification": "Confirmed suspicious activity. IP needs blocking at firewall.",
        },
        headers=auth_headers,
    )
    
    assert response.status_code == 201
    data = response.json()
    assert data["action"] == "ESCALATE"
    assert "justification" in data
    assert "decision_timestamp" in data


@pytest.mark.asyncio
async def test_decision_updates_alert_status(client: AsyncClient, auth_headers):
    """Test that decisions update alert status."""
    alert_id = await create_alert(client, auth_headers)
    
    if alert_id is None:
        pytest.skip("No alert was created")
    
    # Create DISMISS decision (maps to accept -> RESOLVED)
    await client.post(
        f"/api/v1/alerts/{alert_id}/decisions",
        json={
            "action": "DISMISS",
            "justification": "Verified threat has been contained successfully.",
        },
        headers=auth_headers,
    )
    
    # Check alert status changed to RESOLVED
    response = await client.get(f"/api/v1/alerts/{alert_id}", headers=auth_headers)
    assert response.json()["status"] == "RESOLVED"


@pytest.mark.asyncio
async def test_reject_decision_marks_false_positive(client: AsyncClient, auth_headers):
    """Test MARK_SAFE decision marks alert as dismissed (false positive)."""
    alert_id = await create_alert(client, auth_headers)
    
    if alert_id is None:
        pytest.skip("No alert was created")
    
    # Create MARK_SAFE decision (maps to reject -> DISMISSED)
    await client.post(
        f"/api/v1/alerts/{alert_id}/decisions",
        json={
            "action": "MARK_SAFE",
            "justification": "Known scanner IP, already whitelisted in system.",
        },
        headers=auth_headers,
    )
    
    # Check alert status changed to DISMISSED
    response = await client.get(f"/api/v1/alerts/{alert_id}", headers=auth_headers)
    assert response.json()["status"] == "DISMISSED"


@pytest.mark.asyncio
async def test_invalid_decision_type(client: AsyncClient, auth_headers):
    """Test invalid decision type is rejected."""
    alert_id = await create_alert(client, auth_headers)
    
    if alert_id is None:
        pytest.skip("No alert was created")
    
    response = await client.post(
        f"/api/v1/alerts/{alert_id}/decisions",
        json={
            "action": "INVALID_TYPE",
            "justification": "Test invalid action payload.",
        },
        headers=auth_headers,
    )
    
    assert response.status_code == 422  # Validation error



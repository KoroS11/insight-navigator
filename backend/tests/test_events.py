"""
Tests for Event Pipeline (Layers 1-6)
"""
import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_ingest_event(client: AsyncClient, auth_headers):
    """Test event ingestion through the pipeline."""
    from datetime import datetime, timezone
    
    event_data = {
        "event_type": "network_connection",
        "source_ip": "192.168.1.100",
        "dest_ip": "10.0.0.50",
        "dest_port": 443,
        "protocol": "TCP",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "raw_data": {"type": "connection", "status": "established"},
    }
    
    response = await client.post(
        "/api/v1/events/",
        json=event_data,
        headers=auth_headers,
    )
    
    assert response.status_code == 201
    data = response.json()
    
    # Verify pipeline result
    assert "event_id" in data
    assert "processed_event_id" in data
    assert "anomaly_score" in data
    assert isinstance(data["anomaly_score"], float)
    assert 0.0 <= data["anomaly_score"] <= 1.0
    assert "rules_matched" in data
    assert isinstance(data["rules_matched"], list)
    assert "processing_time_ms" in data


@pytest.mark.asyncio
async def test_ingest_suspicious_event(client: AsyncClient, auth_headers):
    """Test ingesting an event that should trigger an alert."""
    # External IP to internal destination on high port during off-hours
    event_data = {
        "event_type": "auth_failure",
        "source_ip": "203.0.113.50",  # External IP
        "dest_ip": "192.168.1.10",    # Internal IP
        "dest_port": 8888,            # High port
        "protocol": "TCP",
        "timestamp": "2024-01-15T03:00:00Z",  # Off-hours
        "raw_data": {"attempts": 5, "user": "admin"},
    }
    
    response = await client.post(
        "/api/v1/events/",
        json=event_data,
        headers=auth_headers,
    )
    
    assert response.status_code == 201
    data = response.json()
    
    # This should trigger at least RULE-005 (external to internal)
    # and possibly RULE-003 (unusual port)
    assert len(data["rules_matched"]) > 0
    
    # Should create an alert
    assert data["alert_id"] is not None
    assert data["risk_score"] is not None


@pytest.mark.asyncio
async def test_list_events(client: AsyncClient, auth_headers):
    """Test listing events."""
    # First create an event
    await client.post(
        "/api/v1/events/",
        json={
            "event_type": "test_event",
            "source_ip": "10.0.0.1",
            "dest_ip": "10.0.0.2",
            "protocol": "TCP",
            "timestamp": "2024-01-15T12:00:00Z",
            "raw_data": {"test": "data"},
        },
        headers=auth_headers,
    )
    
    response = await client.get("/api/v1/events/", headers=auth_headers)
    
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 1
    assert response.headers.get("X-Total-Count") is not None


@pytest.mark.asyncio
async def test_get_event(client: AsyncClient, auth_headers):
    """Test getting a specific event."""
    # Create event
    create_response = await client.post(
        "/api/v1/events/",
        json={
            "event_type": "test_event",
            "source_ip": "10.0.0.1",
            "dest_ip": "10.0.0.2",
            "protocol": "TCP",
            "timestamp": "2024-01-15T12:00:00Z",
            "raw_data": {"test": "data"},
        },
        headers=auth_headers,
    )
    event_id = create_response.json()["event_id"]
    
    # Get event
    response = await client.get(f"/api/v1/events/{event_id}", headers=auth_headers)
    
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == event_id
    assert data["event_type"] == "test_event"


@pytest.mark.asyncio
async def test_get_processed_event(client: AsyncClient, auth_headers):
    """Test getting processed event data."""
    # Create event
    create_response = await client.post(
        "/api/v1/events/",
        json={
            "event_type": "network_scan",
            "source_ip": "192.168.1.50",
            "dest_ip": "192.168.1.100",
            "dest_port": 22,
            "protocol": "TCP",
            "timestamp": "2024-01-15T12:00:00Z",
            "raw_data": {"scan_type": "port_scan"},
        },
        headers=auth_headers,
    )
    event_id = create_response.json()["event_id"]
    
    # Get processed event
    response = await client.get(
        f"/api/v1/events/{event_id}/processed",
        headers=auth_headers,
    )
    
    assert response.status_code == 200
    data = response.json()
    assert "parsed_fields" in data
    assert "asset_criticality" in data
    assert "event_hash" in data


@pytest.mark.asyncio
async def test_event_not_found(client: AsyncClient, auth_headers):
    """Test getting nonexistent event returns 404."""
    fake_id = "00000000-0000-0000-0000-000000000000"
    response = await client.get(f"/api/v1/events/{fake_id}", headers=auth_headers)
    
    assert response.status_code == 404



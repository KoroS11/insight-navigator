"""
Tests for System Endpoints
"""
import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_health_check_public(client: AsyncClient):
    """Test health check is publicly accessible."""
    response = await client.get("/api/v1/system/health")
    
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "timestamp" in data
    assert "metrics" in data


@pytest.mark.asyncio
async def test_root_health(client: AsyncClient):
    """Test root health endpoint for load balancers."""
    response = await client.get("/health")
    
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


@pytest.mark.asyncio
async def test_root_endpoint(client: AsyncClient):
    """Test root endpoint returns API info."""
    response = await client.get("/")
    
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "NSA-X API"
    assert "version" in data
    assert "docs" in data


@pytest.mark.asyncio
async def test_list_rules(client: AsyncClient, auth_headers, default_rules):
    """Test listing security rules."""
    response = await client.get("/api/v1/system/rules", headers=auth_headers)
    
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 5  # Default rules
    
    # Verify rule structure
    rule = data[0]
    assert "rule_id" in rule
    assert "name" in rule
    assert "category" in rule
    assert "severity" in rule
    assert "enabled" in rule


@pytest.mark.asyncio
async def test_get_specific_rule(client: AsyncClient, auth_headers, default_rules):
    """Test getting a specific rule."""
    response = await client.get("/api/v1/system/rules/RULE-001", headers=auth_headers)
    
    assert response.status_code == 200
    data = response.json()
    assert data["rule_id"] == "RULE-001"
    assert data["name"] == "Off-hours service account usage"


@pytest.mark.asyncio
async def test_rules_require_auth(client: AsyncClient):
    """Test rules endpoint requires authentication."""
    response = await client.get("/api/v1/system/rules")
    
    assert response.status_code == 401



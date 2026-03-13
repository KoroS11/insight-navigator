"""
NSA-X Test Configuration
Pytest fixtures and test utilities.
"""
import os

# Set test environment variables BEFORE any app imports
# This must happen before importing any app modules to ensure settings are correct
os.environ.setdefault("DEBUG", "true")
os.environ.setdefault("JWT_SECRET_KEY", "test-secret-key-for-unit-tests-only-min-32-chars")
os.environ.setdefault("DEFAULT_ADMIN_USERNAME", "testadmin")
os.environ.setdefault("DEFAULT_ADMIN_PASSWORD", "testpassword123!")
os.environ.setdefault("DATABASE_URL", "sqlite+aiosqlite:///:memory:")

import uuid
from datetime import datetime, timezone
from typing import AsyncGenerator

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.core import Base, get_db
from app.core.security import get_password_hash
from app.main import app
from app.models import User

# Test database URL (in-memory SQLite)
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"


@pytest_asyncio.fixture
async def async_engine():
    """Create async engine for tests."""
    engine = create_async_engine(
        TEST_DATABASE_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    yield engine
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    
    await engine.dispose()


@pytest_asyncio.fixture
async def db_session(async_engine) -> AsyncGenerator[AsyncSession, None]:
    """Create a test database session."""
    async_session = sessionmaker(
        async_engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )
    
    async with async_session() as session:
        yield session
        await session.rollback()


@pytest_asyncio.fixture
async def client(db_session: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    """Create test client with database session override."""
    
    async def override_get_db():
        yield db_session
    
    app.dependency_overrides[get_db] = override_get_db
    
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac
    
    app.dependency_overrides.clear()


@pytest_asyncio.fixture
async def default_rules(db_session: AsyncSession):
    """Ensure default rules exist in test database."""
    from app.services import SymbolicReasoningService
    
    service = SymbolicReasoningService(db_session)
    await service.ensure_default_rules()
    await db_session.commit()


@pytest_asyncio.fixture
async def test_user(db_session: AsyncSession) -> User:
    """Create a test user."""
    user = User(
        id=uuid.uuid4(),
        username="testuser",
        hashed_password=get_password_hash("testpassword123"),
        full_name="Test User",
        role="analyst",
        is_active=True,
        created_at=datetime.now(timezone.utc),
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user


@pytest_asyncio.fixture
async def auth_headers(client: AsyncClient, test_user: User) -> dict:
    """Get authentication headers for test user."""
    response = await client.post(
        "/api/v1/auth/token",
        data={"username": "testuser", "password": "testpassword123"},
    )
    if response.status_code == 200:
        token = response.json()["access_token"]
        return {"Authorization": f"Bearer {token}"}
    else:
        # Fallback: create token directly
        from app.core.security import create_access_token
        token = create_access_token(username=test_user.username)
        return {"Authorization": f"Bearer {token}"}


@pytest_asyncio.fixture
async def test_admin(db_session: AsyncSession) -> User:
    """Create a test admin user."""
    user = User(
        id=uuid.uuid4(),
        username="admin",
        hashed_password=get_password_hash("adminpassword123"),
        full_name="Test Admin",
        role="admin",
        is_active=True,
        created_at=datetime.now(timezone.utc),
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user


@pytest_asyncio.fixture
async def admin_headers(client: AsyncClient, test_admin: User) -> dict:
    """Get authentication headers for admin user."""
    from app.core.security import create_access_token
    token = create_access_token(username=test_admin.username)
    return {"Authorization": f"Bearer {token}"}


# Test data fixtures
@pytest.fixture
def sample_event_data() -> dict:
    """Sample event data for testing."""
    return {
        "event_type": "network_connection",
        "source_ip": "192.168.1.100",
        "dest_ip": "10.0.0.50",
        "dest_port": 443,
        "protocol": "TCP",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "raw_data": {
            "bytes_sent": 1500,
            "bytes_received": 3000,
            "status": "established",
        },
    }


@pytest.fixture
def sample_malicious_event_data() -> dict:
    """Sample malicious event data for testing."""
    return {
        "event_type": "network_connection",
        "source_ip": "203.0.113.50",  # External
        "dest_ip": "192.168.1.10",    # Internal
        "dest_port": 4444,             # Known malicious port
        "protocol": "TCP",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "raw_data": {
            "bytes_sent": 5000,
            "bytes_received": 15000,
            "suspicious": True,
        },
    }


@pytest.fixture
def sample_decision_data() -> dict:
    """Sample decision data for testing."""
    return {
        "action": "DISMISS",
        "justification": "After thorough investigation, this event represents a legitimate security threat requiring immediate action.",
        "confidence": 0.95,
    }


# Custom markers
def pytest_configure(config):
    """Configure custom pytest markers."""
    config.addinivalue_line(
        "markers", "slow: marks tests as slow (deselect with '-m \"not slow\"')"
    )
    config.addinivalue_line(
        "markers", "integration: marks tests as integration tests"
    )
    config.addinivalue_line(
        "markers", "e2e: marks tests as end-to-end tests"
    )
    config.addinivalue_line(
        "markers", "security: marks tests as security-related"
    )
    config.addinivalue_line(
        "markers", "critical: marks tests as critical/must-pass"
    )


# Test helpers class
class TestHelpers:
    """Helper methods for tests."""
    
    @staticmethod
    def generate_unique_ip() -> str:
        """Generate a unique IP address for testing."""
        import random
        return f"{random.randint(1, 254)}.{random.randint(0, 255)}.{random.randint(0, 255)}.{random.randint(1, 254)}"
    
    @staticmethod
    def generate_event_data(
        event_type: str = "test",
        source_ip: str = None,
        dest_ip: str = "10.0.0.1",
        dest_port: int = 443,
        protocol: str = "TCP",
        timestamp: str = None,
        raw_data: dict = None,
    ) -> dict:
        """Generate valid event data with all required fields."""
        return {
            "event_type": event_type,
            "source_ip": source_ip or TestHelpers.generate_unique_ip(),
            "dest_ip": dest_ip,
            "dest_port": dest_port,
            "protocol": protocol,
            "timestamp": timestamp or datetime.now(timezone.utc).isoformat(),
            "raw_data": raw_data or {},
        }


@pytest.fixture
def helpers() -> TestHelpers:
    """Provide test helpers."""
    return TestHelpers()



"""
NSA-X FastAPI Application Entry Point
Neuro-Symbolic Autonomous Security Analyst
"""
import logging
import time
import uuid
from contextlib import asynccontextmanager
from typing import Any

from fastapi import FastAPI, HTTPException, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app import __version__
from app.core import Base, engine, settings
from app.core.config import get_validated_settings
from app.core.security import get_password_hash
from app.routers import (
    alerts_router,
    audit_router,
    auth_router,
    events_router,
    system_router,
)
from app.models import User
from app.services import SymbolicReasoningService
from app.core.database import async_session_maker

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler."""
    # Startup - validate settings first
    logger.info(f"Starting NSA-X Backend v{__version__}")
    
    # Validate settings (will exit if invalid in non-debug mode)
    get_validated_settings()
    
    logger.info(f"Debug mode: {settings.debug}")
    
    # Create tables (for development; use Alembic in production)
    if settings.debug:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        logger.info("Database tables created/verified (debug mode)")
    
    # Initialize default rules once at startup
    async with async_session_maker() as session:
        service = SymbolicReasoningService(session)
        await service.ensure_default_rules()
        await session.commit()
        logger.info("Default security rules initialized")
    
    # Create default admin user if it doesn't exist
    async with async_session_maker() as session:
        from sqlalchemy import select
        from sqlalchemy.exc import IntegrityError
        result = await session.execute(
            select(User).where(User.username == settings.default_admin_username)
        )
        existing_user = result.scalar_one_or_none()
        
        if not existing_user:
            import uuid
            from datetime import datetime, timezone
            admin_user = User(
                id=str(uuid.uuid4()),
                username=settings.default_admin_username,
                hashed_password=get_password_hash(settings.default_admin_password.get_secret_value()),
                full_name="System Administrator",
                role="admin",
                is_active=True,
                created_at=datetime.now(timezone.utc),
            )
            session.add(admin_user)
            try:
                await session.commit()
                logger.info(f"Default admin user '{settings.default_admin_username}' created")
            except IntegrityError:
                await session.rollback()
                logger.info(f"Admin user '{settings.default_admin_username}' already exists (concurrent create)")
        else:
            logger.info(f"Admin user '{settings.default_admin_username}' already exists")
    
    yield
    
    # Shutdown
    logger.info("Shutting down NSA-X Backend")
    await engine.dispose()


# Create FastAPI application
app = FastAPI(
    title="NSA-X API",
    description="""
    Neuro-Symbolic Autonomous Security Analyst API
    
    A 7-layer architecture combining neural anomaly detection with
    symbolic rule-based reasoning for explainable security analytics.
    
    ## Layers
    
    1. **Data Ingestion** - Raw event storage
    2. **Event Processing** - Normalization and enrichment
    3. **Neural Detection** - Anomaly scoring
    4. **Symbolic Reasoning** - Rule evaluation
    5. **Reasoning Integration** - Alert generation
    6. **Explainability Engine** - Human-readable explanations
    7. **Analyst Decision** - Immutable decision records
    """,
    version=__version__,
    docs_url="/docs" if settings.debug else None,
    redoc_url="/redoc" if settings.debug else None,
    lifespan=lifespan,
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Request timing middleware
@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    """Add X-Process-Time header to all responses."""
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = f"{process_time:.4f}"
    return response


# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Handle uncaught exceptions."""
    if isinstance(exc, HTTPException):
        return JSONResponse(
            status_code=exc.status_code,
            content={"detail": exc.detail},
            headers=exc.headers,
        )

    if isinstance(exc, RequestValidationError):
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={"detail": exc.errors()},
        )

    # Generate correlation ID for traceability
    correlation_id = str(uuid.uuid4())[:8]
    
    # Log the full exception with traceback
    logger.exception(
        f"Unhandled exception [correlation_id={correlation_id}] "
        f"path={request.url.path} method={request.method}: {exc}"
    )
    
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "detail": "Internal server error",
            "correlation_id": correlation_id,
        },
    )


# Include routers
app.include_router(auth_router, prefix="/api/v1")
app.include_router(events_router, prefix="/api/v1")
app.include_router(alerts_router, prefix="/api/v1")
app.include_router(system_router, prefix="/api/v1")
app.include_router(audit_router, prefix="/api/v1")


# Root endpoint
@app.get("/", tags=["root"])
async def root() -> dict[str, Any]:
    """Root endpoint with API information."""
    response = {
        "name": "NSA-X API",
        "version": __version__,
        "description": "Neuro-Symbolic Autonomous Security Analyst",
        "health": "/api/v1/system/health",
    }
    
    # Only include docs URL when documentation is enabled
    if settings.debug:
        response["docs"] = "/docs"
    
    return response


# Health endpoint at root level (for load balancers)
@app.get("/health", tags=["health"])
async def root_health() -> dict[str, str]:
    """Simple health check for load balancers."""
    return {"status": "ok"}

"""
NSA-X Routers Module
Exports all API routers.
"""
from app.routers.alerts import router as alerts_router
from app.routers.audit import router as audit_router
from app.routers.auth import router as auth_router
from app.routers.events import router as events_router
from app.routers.system import router as system_router

__all__ = [
    "alerts_router",
    "audit_router",
    "auth_router",
    "events_router",
    "system_router",
]

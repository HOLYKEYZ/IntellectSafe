from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from sqlmodel import SQLModel

from app.api.routes import agent, audit, scan, governance, proxy, auth
from app.api.middleware.rate_limit import RateLimitMiddleware
from app.db.session import engine
from app.models.database import Base
from app.core.config import get_settings

settings = get_settings()

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Create tables on startup (both SQLModel and SQLAlchemy models)
    SQLModel.metadata.create_all(engine)   # User table
    Base.metadata.create_all(engine)        # scan_requests, risk_scores, audit_logs, etc.
    yield

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="IntellectSafe - AI Safety & Security Platform",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

import logging
logger = logging.getLogger(__name__)

# CORS middleware
logger.info(f"CORS Origins: {settings.cors_origins_list}")
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Rate limiting middleware
if settings.RATE_LIMIT_ENABLED:
    app.add_middleware(RateLimitMiddleware)

# Include routers
app.include_router(auth.router, prefix=f"{settings.API_V1_PREFIX}/auth", tags=["auth"])
app.include_router(scan.router, prefix=settings.API_V1_PREFIX)
app.include_router(agent.router, prefix=settings.API_V1_PREFIX)
app.include_router(audit.router, prefix=settings.API_V1_PREFIX)
app.include_router(governance.router, prefix=settings.API_V1_PREFIX)

# Proxy router - No prefix for OpenAI compatibility (/v1/chat/completions)
app.include_router(proxy.router)

@app.get("/")
async def root():
    return {
        "message": f"Welcome to {settings.APP_NAME}",
        "version": settings.APP_VERSION,
        "docs": "/docs",
        "status": "online"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8001, reload=True)

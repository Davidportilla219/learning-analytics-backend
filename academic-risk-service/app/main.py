"""
Academic Risk Service for the Learning Analytics Platform.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.api.endpoints import health, risk
from app.database import init_db

# Create FastAPI app
app = FastAPI(
    title="Learning Analytics Platform - Academic Risk Service",
    description="Predict academic risk using heuristics and machine learning",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=settings.CORS_ALLOW_CREDENTIALS,
    allow_methods=settings.CORS_ALLOW_METHODS,
    allow_headers=settings.CORS_ALLOW_HEADERS,
)

# Include routers
app.include_router(health.router, prefix="/api/v1", tags=["health"])
app.include_router(risk.router, prefix="/api/v1", tags=["risk"])


@app.on_event("startup")
async def startup_event():
    await init_db()


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "Learning Analytics Platform - Academic Risk Service",
        "version": "1.0.0",
        "docs": "/docs"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8004,
        reload=settings.DEBUG,
        log_level="info"
    )
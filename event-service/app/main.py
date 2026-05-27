"""
FastAPI application for the Event Capture Service.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.api.endpoints import health, events
from app.database import init_db
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create database tables (will be done in startup)
# Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Event Capture Service",
    description="Service for capturing and processing learning analytics events",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_HOSTS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(health.router, prefix="/api/v1", tags=["health"])
app.include_router(events.router, prefix="/api/v1", tags=["events"])

@app.on_event("startup")
async def startup_event():
    """Startup event handler."""
    await init_db()
    logger.info("Event Capture Service starting up...")

@app.on_event("shutdown")
async def shutdown_event():
    """Shutdown event handler."""
    logger.info("Event Capture Service shutting down...")

@app.get("/")
async def root():
    """Root endpoint."""
    return {"message": "Event Capture Service is running"}

@app.get("/status")
async def status():
    """Service status endpoint."""
    return {
        "service": "Event Capture Service",
        "status": "healthy",
        "version": "1.0.0"
    }

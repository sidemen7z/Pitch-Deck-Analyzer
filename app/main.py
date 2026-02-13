from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.models.database import init_db
from app.utils.logging import get_logger
from app.api import documents
import os

logger = get_logger(__name__)

app = FastAPI(
    title="Pitch Deck Analyzer",
    description="AI-powered NLP system for extracting structured information from pitch decks",
    version=settings.system_version
)

# CORS middleware for React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(documents.router)


@app.on_event("startup")
async def startup_event():
    """Initialize application on startup"""
    logger.info("Starting Pitch Deck Analyzer...")
    
    # Create directories
    os.makedirs(settings.upload_dir, exist_ok=True)
    os.makedirs(settings.output_dir, exist_ok=True)
    
    # Initialize database
    await init_db()
    logger.info("MongoDB initialized")
    
    logger.info("Application started successfully")


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    from app.models.database import close_db
    await close_db()
    logger.info("Application shutdown complete")


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Pitch Deck Analyzer API",
        "version": settings.system_version,
        "status": "running"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}

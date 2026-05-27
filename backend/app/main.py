"""
FastAPI application factory.

This is the entry point for the backend. It wires up all the routers,
middleware, and CORS configuration. Run with:
    uvicorn app.main:app --reload
"""

import os
import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import get_settings
from app.database import engine, Base
from app.core.middleware import ActivityLoggingMiddleware
from app.api import auth, tasks, documents, search, analytics

# Import all models so SQLAlchemy knows about them when creating tables
from app.models import Role, User, Task, Document, ActivityLog

settings = get_settings()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


def create_app() -> FastAPI:
    """Build and configure the FastAPI application."""

    app = FastAPI(
        title=settings.APP_NAME,
        description="AI-Powered Task and Knowledge Management System",
        version="1.0.0",
        docs_url="/docs",
        redoc_url="/redoc",
    )

    # -- CORS --
    # In production you'd restrict this, but for development we allow
    # the React dev server to talk to the API without issues.
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["http://localhost:5173", "http://localhost:3000"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # -- Activity logging middleware --
    app.add_middleware(ActivityLoggingMiddleware)

    # -- Routers --
    app.include_router(auth.router, prefix="/api")
    app.include_router(tasks.router, prefix="/api")
    app.include_router(documents.router, prefix="/api")
    app.include_router(search.router, prefix="/api")
    app.include_router(analytics.router, prefix="/api")

    @app.on_event("startup")
    async def startup():
        """Create database tables if they don't exist yet."""
        logger.info("Creating database tables...")
        Base.metadata.create_all(bind=engine)

        # Make sure the uploads directory exists
        os.makedirs(settings.UPLOAD_DIR, exist_ok=True)

        logger.info("Application startup complete")

    @app.get("/", tags=["Health"])
    def health_check():
        """Simple health check endpoint to verify the API is running."""
        return {
            "status": "healthy",
            "app": settings.APP_NAME,
            "version": "1.0.0",
        }

    return app


app = create_app()

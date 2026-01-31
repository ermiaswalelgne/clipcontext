"""
ClipContext API
Find any topic in any YouTube video instantly.
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import search, health
from app.config import settings


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown events."""
    # Startup: Load embedding model
    print("🚀 Starting ClipContext API...")
    print(f"📦 Environment: {settings.environment}")
    
    # TODO: Initialize embedding model here
    # from app.services.embedding import EmbeddingService
    # app.state.embedding_service = EmbeddingService()
    
    yield
    
    # Shutdown
    print("👋 Shutting down ClipContext API...")


app = FastAPI(
    title="ClipContext API",
    description="Find any topic in any YouTube video instantly.",
    version="0.1.0",
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

# Include routers
app.include_router(health.router, tags=["Health"])
app.include_router(search.router, prefix="/api", tags=["Search"])


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "name": "ClipContext API",
        "version": "0.1.0",
        "docs": "/docs",
        "health": "/health",
    }

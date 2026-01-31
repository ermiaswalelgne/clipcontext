"""
Health check endpoints.
"""

from fastapi import APIRouter

router = APIRouter()


@router.get("/health")
async def health_check():
    """Basic health check."""
    return {
        "status": "healthy",
        "service": "clipcontext-api",
    }


@router.get("/health/ready")
async def readiness_check():
    """
    Readiness check for Kubernetes.
    Verifies all dependencies are available.
    """
    # TODO: Check database connection
    # TODO: Check Redis connection
    # TODO: Check embedding model loaded
    
    return {
        "status": "ready",
        "checks": {
            "database": "ok",  # TODO: Implement actual check
            "cache": "ok",     # TODO: Implement actual check
            "model": "ok",     # TODO: Implement actual check
        }
    }


@router.get("/health/live")
async def liveness_check():
    """
    Liveness check for Kubernetes.
    Simple check that the service is running.
    """
    return {"status": "alive"}

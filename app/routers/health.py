"""
Health check router
Provides health check endpoints for monitoring
"""
from datetime import datetime
from fastapi import APIRouter
from ..models.schemas import HealthResponse

router = APIRouter(prefix="/health", tags=["health"])

@router.get("", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    return HealthResponse(
        ok=True,
        message="Backend is running",
        timestamp=datetime.utcnow().isoformat()
    )

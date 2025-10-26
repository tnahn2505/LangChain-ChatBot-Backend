"""
Health routes - GET /health
"""
from fastapi import APIRouter
from pydantic import BaseModel
from typing import Optional

router = APIRouter()

class HealthResponse(BaseModel):
    ok: bool
    message: Optional[str] = None
    timestamp: Optional[str] = None

@router.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    from datetime import datetime
    
    return HealthResponse(
        ok=True,
        message="Backend is running",
        timestamp=datetime.utcnow().isoformat()
    )

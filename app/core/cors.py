"""
CORS configuration module
Handles Cross-Origin Resource Sharing settings based on environment configuration
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .config import get_settings

def setup_cors(app: FastAPI) -> None:
    """Setup CORS middleware based on environment configuration"""
    settings = get_settings()
    
    # Parse comma-separated origins
    origins = [origin.strip() for origin in settings.cors_allowed_origins.split(",")]
    
    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=settings.cors_allow_credentials,
        allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        allow_headers=["*"],
        expose_headers=["*"],
    )

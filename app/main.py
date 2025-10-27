"""
Main FastAPI application
Entry point with proper lifespan management and router inclusion
"""
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .core.config import get_settings
from .core.cors import setup_cors
from .db.mongo import mongodb
from .db.mongo_indexes import create_indexes
from .routers import health, threads, messages

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    # Startup
    print("Starting ChatBot Backend...")
    
    # Connect to MongoDB
    await mongodb.connect()
    
    # Create database indexes
    await create_indexes(mongodb.get_database())
    
    print("Success: Backend startup completed")
    
    yield
    
    # Shutdown
    print("Shutting down ChatBot Backend...")
    await mongodb.disconnect()
    print("Success: Backend shutdown completed")

# Get settings
settings = get_settings()

# Create FastAPI app
app = FastAPI(
    title=settings.app_name,
    description="Backend API for ChatBot application with LangChain integration",
    version=settings.app_version,
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# Setup CORS
setup_cors(app)

# Include routers
app.include_router(health.router)
app.include_router(threads.router)
app.include_router(messages.router)

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": settings.app_name,
        "version": settings.app_version,
        "docs": "/docs",
        "health": "/health",
        "status": "running"
    }

if __name__ == "__main__":
    import uvicorn
    
    print(f"Host: {settings.host}")
    print(f"Port: {settings.port}")
    print(f"Reload: {settings.reload}")
    print(f"API Docs: http://{settings.host}:{settings.port}/docs")
    print(f"Health: http://{settings.host}:{settings.port}/health")
    print("-" * 50)
    
    uvicorn.run(
        "app.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.reload,
        log_level="info"
    )

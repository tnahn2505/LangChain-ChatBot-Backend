"""
FastAPI Main Application - Following Architecture Document
"""
import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

# Import routes
from routes.health import router as health_router
from routes.threads import router as threads_router
from routes.messages import router as messages_router

# Load environment variables
load_dotenv()

# Initialize FastAPI app
app = FastAPI(
    title="ChatBot Backend API",
    description="Backend API for ChatBot application - Following Architecture Document",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(health_router, tags=["Health"])
app.include_router(threads_router, tags=["Threads"])
app.include_router(messages_router, tags=["Messages"])

# Root endpoint
@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "ChatBot Backend API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health",
        "architecture": "Following FE Architecture Document"
    }

if __name__ == "__main__":
    import uvicorn
    
    # Get configuration from environment
    host = os.getenv("HOST", "127.0.0.1")
    port = int(os.getenv("PORT", "8000"))
    reload = os.getenv("RELOAD", "true").lower() == "true"
    
    print("Starting ChatBot Backend...")
    print(f"Host: {host}")
    print(f"Port: {port}")
    print(f"Reload: {reload}")
    print(f"API Docs: http://{host}:{port}/docs")
    print(f"Health: http://{host}:{port}/health")
    print("Architecture: Following FE Architecture Document")
    print("-" * 50)
    
    uvicorn.run(
        "main:app",
        host=host,
        port=port,
        reload=reload,
        log_level="info"
    )

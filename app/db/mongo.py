"""
MongoDB connection and database management
Handles Motor client connection, database access, and connection lifecycle
"""
from typing import Optional
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from ..core.config import get_settings

class MongoDB:
    """MongoDB connection manager"""
    
    def __init__(self):
        self.client: Optional[AsyncIOMotorClient] = None
        self.database: Optional[AsyncIOMotorDatabase] = None
        self.settings = get_settings()
    
    async def connect(self) -> None:
        """Create database connection"""
        try:
            self.client = AsyncIOMotorClient(self.settings.mongodb_uri)
            self.database = self.client[self.settings.mongodb_db_name]
            
            # Test connection
            await self.client.admin.command('ping')
            print(f"Success: Connected to MongoDB: {self.settings.mongodb_db_name}")
            
        except Exception as e:
            print(f"Error: Failed to connect to MongoDB: {e}")
            raise
    
    async def disconnect(self) -> None:
        """Close database connection"""
        if self.client:
            self.client.close()
            print("MongoDB connection closed")
    
    def get_database(self) -> AsyncIOMotorDatabase:
        """Get database instance"""
        if self.database is None:
            raise RuntimeError("Database not connected. Call connect() first.")
        return self.database

# Global MongoDB instance
mongodb = MongoDB()

async def get_db() -> AsyncIOMotorDatabase:
    """FastAPI dependency to get database instance"""
    return mongodb.get_database()

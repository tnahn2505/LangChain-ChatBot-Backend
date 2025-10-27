"""
MongoDB indexes creation
Creates necessary indexes for optimal performance on threads and messages collections
"""
from motor.motor_asyncio import AsyncIOMotorDatabase
from ..core.config import get_settings

async def create_indexes(database: AsyncIOMotorDatabase) -> None:
    """Create database indexes for better performance"""
    settings = get_settings()
    
    try:
        # Threads collection indexes
        await database.threads.create_index("id", unique=True)
        await database.threads.create_index("updatedAt")
        await database.threads.create_index("createdAt")
        
        # Messages collection indexes
        await database.messages.create_index("id", unique=True)
        await database.messages.create_index("threadId")
        await database.messages.create_index("createdAt")
        await database.messages.create_index([("threadId", 1), ("createdAt", 1)])
        await database.messages.create_index("role")
        
        print("Success: Database indexes created successfully")
        
    except Exception as e:
        print(f"Error: Failed to create indexes: {e}")
        raise

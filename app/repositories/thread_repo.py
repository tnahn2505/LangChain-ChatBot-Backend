"""
Thread repository
Handles all database operations related to threads
"""
from datetime import datetime
from typing import List, Optional
from motor.motor_asyncio import AsyncIOMotorDatabase
from ..models.schemas import ThreadDocument, ThreadOut
from ..core.config import get_settings

class ThreadRepository:
    """Repository for thread-related database operations"""
    
    def __init__(self, database: AsyncIOMotorDatabase):
        self.database = database
        self.settings = get_settings()
    
    async def create_thread(self, thread_id: str, title: str) -> ThreadDocument:
        """Create a new thread"""
        now = datetime.utcnow().isoformat()
        thread_doc = ThreadDocument(
            id=thread_id,
            title=title,
            createdAt=now,
            updatedAt=now
        )
        
        await self.database.threads.insert_one(thread_doc.dict())
        return thread_doc
    
    async def get_thread(self, thread_id: str) -> Optional[ThreadDocument]:
        """Get a thread by ID"""
        thread_doc = await self.database.threads.find_one({"id": thread_id})
        if thread_doc:
            return ThreadDocument(**thread_doc)
        return None
    
    async def get_threads(
        self, 
        skip: int = 0, 
        limit: int = 50
    ) -> List[ThreadDocument]:
        """Get all threads with pagination"""
        cursor = self.database.threads.find().skip(skip).limit(limit).sort("updatedAt", -1)
        threads = []
        
        async for thread_doc in cursor:
            threads.append(ThreadDocument(**thread_doc))
        
        return threads
    
    async def update_thread(self, thread_id: str, title: str = None) -> bool:
        """Update thread title or just timestamp"""
        update_data = {"updatedAt": datetime.utcnow().isoformat()}
        if title is not None:
            update_data["title"] = title
            
        result = await self.database.threads.update_one(
            {"id": thread_id},
            {"$set": update_data}
        )
        return result.matched_count > 0
    
    async def delete_thread(self, thread_id: str) -> bool:
        """Delete a thread"""
        result = await self.database.threads.delete_one({"id": thread_id})
        return result.deleted_count > 0
    
    async def count_threads(self) -> int:
        """Count total number of threads"""
        return await self.database.threads.count_documents({})
    
    async def get_thread_with_message_count(self, thread_id: str) -> Optional[ThreadOut]:
        """Get thread with message count"""
        thread_doc = await self.get_thread(thread_id)
        if not thread_doc:
            return None
        
        # Count messages for this thread
        messages_count = await self.database.messages.count_documents({"threadId": thread_id})
        
        return ThreadOut(
            id=thread_doc.id,
            title=thread_doc.title,
            updatedAt=thread_doc.updatedAt,
            createdAt=thread_doc.createdAt,
            messagesCount=messages_count
        )

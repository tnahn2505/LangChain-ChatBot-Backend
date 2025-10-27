"""
Message repository
Handles all database operations related to messages and chat history
"""
from datetime import datetime
from typing import List, Optional
from motor.motor_asyncio import AsyncIOMotorDatabase
from ..models.schemas import MessageDocument, MessageOut
from ..core.config import get_settings

class MessageRepository:
    """Repository for message-related database operations"""
    
    def __init__(self, database: AsyncIOMotorDatabase):
        self.database = database
        self.settings = get_settings()
    
    async def create_message(
        self, 
        message_id: str, 
        thread_id: str, 
        role: str, 
        content: str,
        metadata: Optional[dict] = None
    ) -> MessageDocument:
        """Create a new message"""
        now = datetime.utcnow().isoformat()
        message_doc = MessageDocument(
            id=message_id,
            threadId=thread_id,
            role=role,
            content=content,
            createdAt=now,
            metadata=metadata or {}
        )
        
        await self.database.messages.insert_one(message_doc.dict())
        return message_doc
    
    async def get_message(self, message_id: str) -> Optional[MessageDocument]:
        """Get a message by ID"""
        message_doc = await self.database.messages.find_one({"id": message_id})
        if message_doc:
            return MessageDocument(**message_doc)
        return None
    
    async def get_messages(
        self, 
        thread_id: str, 
        skip: int = 0, 
        limit: int = 50
    ) -> List[MessageDocument]:
        """Get messages for a thread with pagination (chronological order)"""
        cursor = (
            self.database.messages
            .find({"threadId": thread_id})
            .skip(skip)
            .limit(limit)
            .sort("createdAt", 1)  # Ascending order (oldest first)
        )
        
        messages = []
        async for message_doc in cursor:
            messages.append(MessageDocument(**message_doc))
        
        return messages
    
    async def get_history(
        self, 
        thread_id: str, 
        limit: int = 15
    ) -> List[MessageDocument]:
        """
        Get chat history for AI context
        Returns messages in chronological order (oldest first) for LangChain
        """
        # Get messages in reverse chronological order (newest first)
        cursor = (
            self.database.messages
            .find({"threadId": thread_id})
            .sort("createdAt", -1)  # Descending order (newest first)
            .limit(limit)
        )
        
        messages = []
        async for message_doc in cursor:
            messages.append(MessageDocument(**message_doc))
        
        # Reverse to get chronological order (oldest first) for LangChain
        messages.reverse()
        return messages
    
    async def count_messages(self, thread_id: str) -> int:
        """Count messages in a thread"""
        return await self.database.messages.count_documents({"threadId": thread_id})
    
    async def delete_messages(self, thread_id: str) -> int:
        """Delete all messages for a thread"""
        result = await self.database.messages.delete_many({"threadId": thread_id})
        return result.deleted_count
    
    async def get_messages_with_pagination(
        self, 
        thread_id: str, 
        skip: int = 0, 
        limit: int = 50
    ) -> tuple[List[MessageOut], int]:
        """Get messages with pagination and return as MessageOut objects"""
        messages = await self.get_messages(thread_id, skip, limit)
        total = await self.count_messages(thread_id)
        
        message_outs = [
            MessageOut(
                id=msg.id,
                role=msg.role,
                content=msg.content,
                createdAt=msg.createdAt
            )
            for msg in messages
        ]
        
        return message_outs, total

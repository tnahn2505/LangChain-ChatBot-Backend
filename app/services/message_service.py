"""
Message Service
Handles all message-related business logic
"""
from typing import List, Tuple
from ..repositories.message_repo import MessageRepository
from ..repositories.thread_repo import ThreadRepository
from ..models.schemas import MessageOut

class MessageService:
    """Service for message-related business logic"""
    
    def __init__(self, message_repo: MessageRepository, thread_repo: ThreadRepository):
        self.message_repo = message_repo
        self.thread_repo = thread_repo
    
    async def get_thread_messages(self, thread_id: str, skip: int = 0, limit: int = 50) -> List[MessageOut]:
        """Get messages for a specific thread"""
        # Verify thread exists
        thread = await self.thread_repo.get_thread(thread_id)
        if not thread:
            return None
        
        # Get messages with pagination
        messages, total = await self.message_repo.get_messages_with_pagination(
            thread_id, skip, limit
        )
        
        return messages
    
    async def get_conversation_history(self, thread_id: str, limit: int = 50) -> List[MessageOut]:
        """Get conversation history for a thread"""
        # Verify thread exists
        thread = await self.thread_repo.get_thread(thread_id)
        if not thread:
            return None
        
        # Get recent messages
        messages, total = await self.message_repo.get_messages_with_pagination(
            thread_id, 0, limit
        )
        
        return messages

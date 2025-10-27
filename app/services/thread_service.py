"""
Thread Service
Handles all thread-related business logic
"""
from datetime import datetime
from typing import List, Optional
from ..repositories.thread_repo import ThreadRepository
from ..repositories.message_repo import MessageRepository
from ..models.schemas import ThreadOut, ThreadCreate, ThreadUpdate, SuccessResponse, ThreadCreateResponse

class ThreadService:
    """Service for thread-related business logic"""
    
    def __init__(self, thread_repo: ThreadRepository, message_repo: MessageRepository):
        self.thread_repo = thread_repo
        self.message_repo = message_repo
    
    async def create_thread(self, title: str) -> ThreadCreateResponse:
        """Create a new thread"""
        # Generate thread ID
        thread_id = f"thread_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}_{datetime.utcnow().microsecond}"
        
        # Create thread
        await self.thread_repo.create_thread(thread_id, title)
        
        # Create welcome message
        await self._create_welcome_message(thread_id)
        
        return ThreadCreateResponse(id=thread_id)
    
    async def get_all_threads(self, skip: int = 0, limit: int = 50) -> List[ThreadOut]:
        """Get all threads with message counts"""
        # Get threads
        threads = await self.thread_repo.get_threads(skip, limit)
        
        # Convert to response format with message counts
        thread_responses = []
        for thread in threads:
            messages_count = await self.thread_repo.database.messages.count_documents({"threadId": thread.id})
            thread_responses.append(ThreadOut(
                id=thread.id,
                title=thread.title,
                updatedAt=thread.updatedAt,
                createdAt=thread.createdAt,
                messagesCount=messages_count
            ))
        
        return thread_responses
    
    async def get_thread(self, thread_id: str) -> Optional[ThreadOut]:
        """Get a specific thread by ID"""
        return await self.thread_repo.get_thread_with_message_count(thread_id)
    
    async def update_thread(self, thread_id: str, title: str) -> SuccessResponse:
        """Update thread title"""
        success = await self.thread_repo.update_thread(thread_id, title)
        if not success:
            return None
        
        return SuccessResponse(
            ok=True,
            message="Thread updated successfully"
        )
    
    async def delete_thread(self, thread_id: str) -> SuccessResponse:
        """Delete a thread and all its messages"""
        # Delete all messages for this thread
        deleted_messages = await self.message_repo.delete_messages(thread_id)
        
        # Delete the thread
        success = await self.thread_repo.delete_thread(thread_id)
        if not success:
            return None
        
        return SuccessResponse(
            ok=True,
            message=f"Thread and {deleted_messages} messages deleted successfully"
        )
    
    async def _create_welcome_message(self, thread_id: str) -> None:
        """Create welcome message for new thread"""
        welcome_message = {
            "id": f"msg_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}_{datetime.utcnow().microsecond}",
            "threadId": thread_id,
            "role": "assistant",
            "content": "Xin chào! Tôi là AI Assistant. Tôi có thể giúp gì cho bạn?",
            "createdAt": datetime.utcnow().isoformat(),
            "metadata": {"type": "welcome"}
        }
        
        await self.message_repo.create_message(welcome_message)

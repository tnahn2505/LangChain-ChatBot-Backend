"""
Chat Service
Handles chat business logic including message processing and AI integration
"""
from datetime import datetime
from typing import Dict, Any, List
from ..repositories.thread_repo import ThreadRepository
from ..repositories.message_repo import MessageRepository
from ..services.ai_service import AIService
from ..models.schemas import SendMessageResponse, MessageDocument
from ..core.config import get_settings

class ChatService:
    """Service for chat-related business logic"""
    
    def __init__(self, thread_repo: ThreadRepository, message_repo: MessageRepository):
        self.thread_repo = thread_repo
        self.message_repo = message_repo
        self.ai_service = AIService()
        self.settings = get_settings()
    
    async def create_welcome_message(self, thread_id: str) -> None:
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
    
    async def send_message(
        self, 
        thread_id: str, 
        content: str, 
        metadata: Dict[str, Any] = None
    ) -> SendMessageResponse:
        """Send a message and get AI response"""
        # Generate message IDs
        now = datetime.utcnow()
        timestamp = now.strftime('%Y%m%d_%H%M%S')
        user_message_id = f"msg_{timestamp}_user_{now.microsecond}"
        assistant_message_id = f"msg_{timestamp}_assistant_{now.microsecond + 1}"
        
        # Get chat history for context
        history = await self._get_chat_history(thread_id)
        
        # Process message with AI (now with thread_id for LangChain memory)
        ai_response = await self.ai_service.process_message(content, thread_id, history)
        
        # Save user message
        user_message = await self.message_repo.create_message(
            message_id=user_message_id,
            thread_id=thread_id,
            role="user",
            content=content,
            metadata=metadata
        )
        
        # Save assistant message
        assistant_message = await self.message_repo.create_message(
            message_id=assistant_message_id,
            thread_id=thread_id,
            role="assistant",
            content=ai_response.content,
            metadata={
                "model": ai_response.model,
                "usage": ai_response.usage.dict(),
                "latency_ms": ai_response.latency_ms
            }
        )
        
        # Update thread timestamp
        await self.thread_repo.update_thread(thread_id, None)  # Update timestamp only
        
        return SendMessageResponse(
            thread_id=thread_id,
            user_message_id=user_message_id,
            assistant_message_id=assistant_message_id,
            assistant={
                "content": ai_response.content,
                "model": ai_response.model,
                "usage": ai_response.usage.dict(),
                "latency_ms": ai_response.latency_ms
            }
        )
    
    async def _get_chat_history(self, thread_id: str) -> List[Dict[str, str]]:
        """Get chat history for AI context"""
        # Get recent messages (limit to max_history_messages)
        messages = await self.message_repo.get_history(
            thread_id, 
            self.settings.max_history_messages
        )
        
        # Convert to format expected by AI service
        history = []
        for msg in messages:
            history.append({
                "role": msg.role,
                "content": msg.content
            })
        
        return history
    
    async def create_welcome_message(self, thread_id: str) -> MessageDocument:
        """Create welcome message for new thread"""
        now = datetime.utcnow()
        timestamp = now.strftime('%Y%m%d_%H%M%S')
        welcome_message_id = f"welcome_{thread_id}_{timestamp}"
        
        welcome_content = (
            "Xin chào! Tôi là AI Assistant. Tôi có thể giúp bạn trả lời câu hỏi, "
            "giải thích khái niệm, hoặc hỗ trợ bạn trong nhiều lĩnh vực khác nhau. "
            "Bạn có câu hỏi gì không?"
        )
        
        return await self.message_repo.create_message(
            message_id=welcome_message_id,
            thread_id=thread_id,
            role="assistant",
            content=welcome_content,
            metadata={"type": "welcome"}
        )

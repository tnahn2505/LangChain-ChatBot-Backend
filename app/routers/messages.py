"""
Messages router
Handles all message-related API endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from motor.motor_asyncio import AsyncIOMotorDatabase

from ..db.mongo import get_db
from ..repositories.thread_repo import ThreadRepository
from ..repositories.message_repo import MessageRepository
from ..services.chat_service import ChatService
from ..models.schemas import (
    SendMessageRequest,
    SendMessageResponse,
    MessageListResponse
)

router = APIRouter(prefix="/messages", tags=["messages"])

def get_thread_repo(db: AsyncIOMotorDatabase = Depends(get_db)) -> ThreadRepository:
    """Dependency to get thread repository"""
    return ThreadRepository(db)

def get_message_repo(db: AsyncIOMotorDatabase = Depends(get_db)) -> MessageRepository:
    """Dependency to get message repository"""
    return MessageRepository(db)

def get_chat_service(
    thread_repo: ThreadRepository = Depends(get_thread_repo),
    message_repo: MessageRepository = Depends(get_message_repo)
) -> ChatService:
    """Dependency to get chat service"""
    return ChatService(thread_repo, message_repo)

@router.post("/send", response_model=SendMessageResponse)
async def send_message(
    message_data: SendMessageRequest,
    thread_id: str = Query(..., description="Thread ID to send message to"),
    chat_service: ChatService = Depends(get_chat_service)
):
    """Send a message to AI"""
    try:
        # Verify thread exists
        thread = await chat_service.thread_repo.get_thread(thread_id)
        if not thread:
            raise HTTPException(status_code=404, detail="Thread not found")
        
        # Send message through chat service
        response = await chat_service.send_message(
            thread_id=thread_id,
            content=message_data.content,
            metadata=message_data.metadata
        )
        
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to send message: {str(e)}")

@router.get("", response_model=MessageListResponse)
async def get_messages(
    thread_id: str = Query(..., description="Thread ID to get messages from"),
    skip: int = Query(0, ge=0, description="Number of messages to skip"),
    limit: int = Query(50, ge=1, le=100, description="Maximum number of messages to return"),
    message_repo: MessageRepository = Depends(get_message_repo)
):
    """Get messages for a specific thread with pagination"""
    try:
        # Verify thread exists
        thread = await message_repo.database.threads.find_one({"id": thread_id})
        if not thread:
            raise HTTPException(status_code=404, detail="Thread not found")
        
        # Get messages with pagination
        messages, total = await message_repo.get_messages_with_pagination(
            thread_id, skip, limit
        )
        
        return MessageListResponse(
            messages=messages,
            total=total,
            skip=skip,
            limit=limit
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get messages: {str(e)}")

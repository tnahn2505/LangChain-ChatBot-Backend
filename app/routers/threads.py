"""
Threads router
Handles all thread-related API endpoints
"""
from datetime import datetime
from typing import List
from fastapi import APIRouter, Depends, HTTPException, Query
from motor.motor_asyncio import AsyncIOMotorDatabase

from ..db.mongo import get_db
from ..repositories.thread_repo import ThreadRepository
from ..repositories.message_repo import MessageRepository
from ..services.chat_service import ChatService
from ..services.thread_service import ThreadService
from ..services.message_service import MessageService
from ..models.schemas import (
    ThreadCreate, 
    ThreadUpdate, 
    ThreadOut, 
    ThreadListResponse, 
    SuccessResponse,
    ThreadCreateResponse,
    SendMessageRequest,
    SendMessageResponse,
    MessageOut 
)

router = APIRouter(prefix="/threads", tags=["threads"])

@router.options("")
@router.options("/{thread_id}")
@router.options("/{thread_id}/messages")
@router.options("/{thread_id}/history")
async def options_threads():
    """Handle CORS preflight requests for threads"""
    return {"message": "OK"}

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

def get_thread_service(
    thread_repo: ThreadRepository = Depends(get_thread_repo),
    message_repo: MessageRepository = Depends(get_message_repo)
) -> ThreadService:
    """Dependency to get thread service"""
    return ThreadService(thread_repo, message_repo)

def get_message_service(
    message_repo: MessageRepository = Depends(get_message_repo),
    thread_repo: ThreadRepository = Depends(get_thread_repo)
) -> MessageService:
    """Dependency to get message service"""
    return MessageService(message_repo, thread_repo)

@router.post("", response_model=ThreadCreateResponse)
async def create_thread(
    thread_data: ThreadCreate,
    thread_service: ThreadService = Depends(get_thread_service)
):
    """Create a new thread"""
    try:
        result = await thread_service.create_thread(thread_data.title)
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create thread: {str(e)}")

@router.get("", response_model=List[ThreadOut])
async def get_all_threads(
    skip: int = Query(0, ge=0, description="Number of threads to skip"),
    limit: int = Query(50, ge=1, le=100, description="Maximum number of threads to return"),
    thread_service: ThreadService = Depends(get_thread_service)
):
    """Get all threads (Frontend compatible - returns Thread[] instead of ThreadListResponse)"""
    try:
        threads = await thread_service.get_all_threads(skip, limit)
        return threads
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get threads: {str(e)}")

@router.get("/{thread_id}", response_model=ThreadOut)
async def get_thread(
    thread_id: str,
    thread_service: ThreadService = Depends(get_thread_service)
):
    """Get a specific thread by ID"""
    try:
        thread = await thread_service.get_thread(thread_id)
        if not thread:
            raise HTTPException(status_code=404, detail="Thread not found")
        
        return thread
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get thread: {str(e)}")

@router.put("/{thread_id}", response_model=SuccessResponse)
async def update_thread(
    thread_id: str,
    thread_data: ThreadUpdate,
    thread_service: ThreadService = Depends(get_thread_service)
):
    """Update thread title"""
    try:
        result = await thread_service.update_thread(thread_id, thread_data.title)
        if not result:
            raise HTTPException(status_code=404, detail="Thread not found")
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update thread: {str(e)}")

@router.delete("/{thread_id}", response_model=SuccessResponse)
async def delete_thread(
    thread_id: str,
    thread_service: ThreadService = Depends(get_thread_service)
):
    """Delete a thread and all its messages"""
    try:
        result = await thread_service.delete_thread(thread_id)
        if not result:
            raise HTTPException(status_code=404, detail="Thread not found")
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete thread: {str(e)}")

@router.post("/{thread_id}/messages", response_model=SendMessageResponse)
async def send_message_to_thread(
    thread_id: str,
    message_data: SendMessageRequest,
    chat_service: ChatService = Depends(get_chat_service)
):
    """Send a message to a specific thread (Frontend compatible endpoint)"""
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

@router.get("/{thread_id}/history", response_model=List[MessageOut])
async def get_conversation_history(
    thread_id: str,
    limit: int = Query(50, ge=1, le=100, description="Maximum number of messages to return"),
    message_service: MessageService = Depends(get_message_service)
):
    """Get conversation history for a thread (History API)"""
    try:
        messages = await message_service.get_conversation_history(thread_id, limit)
        if messages is None:
            raise HTTPException(status_code=404, detail="Thread not found")
        
        return messages
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get conversation history: {str(e)}")

@router.get("/{thread_id}/messages", response_model=List[MessageOut])
async def get_thread_messages(
    thread_id: str,
    skip: int = Query(0, ge=0, description="Number of messages to skip"),
    limit: int = Query(50, ge=1, le=100, description="Maximum number of messages to return"),
    message_service: MessageService = Depends(get_message_service)
):
    """Get messages for a specific thread (Frontend compatible endpoint)"""
    try:
        messages = await message_service.get_thread_messages(thread_id, skip, limit)
        if messages is None:
            raise HTTPException(status_code=404, detail="Thread not found")
        
        return messages
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get messages: {str(e)}")

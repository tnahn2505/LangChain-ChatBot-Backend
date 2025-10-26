"""
Message routes - POST /threads/{id}/messages
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Dict, Any, Optional
from datetime import datetime
import os

router = APIRouter(prefix="/threads")

# Request Models
class MessageCreateRequest(BaseModel):
    content: str = Field(..., min_length=1, max_length=10000, description="Message content")
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Additional metadata")

# Response Models
class SendMessageResponse(BaseModel):
    thread_id: str
    user_message_id: str
    assistant_message_id: str
    assistant: Dict[str, Any]

class MessageResponse(BaseModel):
    id: str
    role: str
    content: str
    createdAt: str

class MessageListResponse(BaseModel):
    messages: list[MessageResponse]
    total: int
    skip: int = 0
    limit: int = 50

@router.post("/{thread_id}/messages", response_model=SendMessageResponse)
async def send_message(thread_id: str, message_data: MessageCreateRequest):
    """Send message to AI - matches frontend api.sendMessage()"""
    try:
        from services.database import get_database
        
        # Generate message IDs (matching frontend format)
        user_message_id = f"msg_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}_user_{os.urandom(4).hex()}"
        assistant_message_id = f"msg_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}_assistant_{os.urandom(4).hex()}"
        
        # Call AI service to get response
        from services.ai_service import AIService
        ai_result = await AIService.process_message(message_data.content)
        ai_response = ai_result["content"]
        
        # Save messages to MongoDB
        db = await get_database()
        
        # Save user message
        user_message = {
            "id": user_message_id,
            "threadId": thread_id,
            "role": "user",
            "content": message_data.content,
            "createdAt": datetime.utcnow().isoformat()
        }
        await db.messages.insert_one(user_message)
        
        # Save assistant message
        assistant_message = {
            "id": assistant_message_id,
            "threadId": thread_id,
            "role": "assistant",
            "content": ai_response,
            "createdAt": datetime.utcnow().isoformat()
        }
        await db.messages.insert_one(assistant_message)
        
        # Update thread updatedAt
        await db.threads.update_one(
            {"id": thread_id},
            {"$set": {"updatedAt": datetime.utcnow().isoformat()}}
        )
        
        return SendMessageResponse(
            thread_id=thread_id,
            user_message_id=user_message_id,
            assistant_message_id=assistant_message_id,
            assistant={
                "content": ai_response,
                "model": ai_result.get("model", "gpt-3.5-turbo"),
                "usage": ai_result.get("usage", {
                    "prompt_tokens": 0,
                    "completion_tokens": 0,
                    "total_tokens": 0
                })
            }
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to send message: {str(e)}")

@router.get("/{thread_id}/messages", response_model=list[MessageResponse])
async def get_messages(thread_id: str, skip: int = 0, limit: int = 50):
    """Get messages for a specific thread with pagination"""
    try:
        from services.database import get_database
        
        # Query MongoDB
        db = await get_database()
        cursor = db.messages.find({"threadId": thread_id}).skip(skip).limit(limit).sort("createdAt", 1)
        messages = []
        
        async for message_doc in cursor:
            messages.append(MessageResponse(
                id=message_doc["id"],
                role=message_doc["role"],
                content=message_doc["content"],
                createdAt=message_doc["createdAt"]
            ))
        
        return messages
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get messages: {str(e)}")

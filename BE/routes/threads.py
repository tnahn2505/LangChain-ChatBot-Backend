"""
Thread routes - POST /threads, GET /threads
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime
import os

router = APIRouter()

# Request Models
class ThreadCreateRequest(BaseModel):
    title: str = Field(..., min_length=1, max_length=200, description="Thread title")

class ThreadUpdateRequest(BaseModel):
    title: str = Field(..., min_length=1, max_length=200, description="New thread title")

# Response Models
class ThreadResponse(BaseModel):
    id: str
    title: str
    updatedAt: str
    createdAt: str
    messagesCount: int = 0

class ThreadListResponse(BaseModel):
    threads: List[ThreadResponse]
    total: int
    skip: int = 0
    limit: int = 50

class SuccessResponse(BaseModel):
    ok: bool
    message: Optional[str] = None

@router.post("/threads", response_model=dict)
async def create_thread(thread_data: ThreadCreateRequest):
    """Create a new thread"""
    try:
        from services.database import get_database
        
        # Generate thread ID (matching frontend format)
        thread_id = f"thread_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}_{os.urandom(4).hex()}"
        
        # Save to MongoDB
        db = await get_database()
        thread_doc = {
            "id": thread_id,
            "title": thread_data.title,
            "createdAt": datetime.utcnow().isoformat(),
            "updatedAt": datetime.utcnow().isoformat()
        }
        
        await db.threads.insert_one(thread_doc)
        
        # Tạo welcome message
        welcome_message = {
            "id": f"welcome_{thread_id}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}",
            "threadId": thread_id,
            "role": "assistant",
            "content": "Xin chào! Tôi là AI Assistant. Tôi có thể giúp bạn trả lời câu hỏi, giải thích khái niệm, hoặc hỗ trợ bạn trong nhiều lĩnh vực khác nhau. Bạn có câu hỏi gì không?",
            "createdAt": datetime.utcnow().isoformat()
        }
        
        await db.messages.insert_one(welcome_message)
        
        return {"id": thread_id}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create thread: {str(e)}")

@router.get("/threads", response_model=List[ThreadResponse])
async def get_all_threads(skip: int = 0, limit: int = 50):
    """Get all threads with pagination"""
    try:
        from services.database import get_database
        
        # Query MongoDB
        db = await get_database()
        cursor = db.threads.find().skip(skip).limit(limit).sort("updatedAt", -1)
        threads = []
        
        async for thread_doc in cursor:
            # Count messages for this thread
            messages_count = await db.messages.count_documents({"threadId": thread_doc["id"]})
            
            threads.append(ThreadResponse(
                id=thread_doc["id"],
                title=thread_doc["title"],
                updatedAt=thread_doc["updatedAt"],
                createdAt=thread_doc["createdAt"],
                messagesCount=messages_count
            ))
        
        return threads
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get threads: {str(e)}")

@router.get("/threads/{thread_id}", response_model=ThreadResponse)
async def get_thread(thread_id: str):
    """Get a specific thread by ID"""
    try:
        # In a real implementation, you would query database
        # For now, return not found
        raise HTTPException(status_code=404, detail="Thread not found")
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get thread: {str(e)}")

@router.put("/threads/{thread_id}", response_model=SuccessResponse)
async def update_thread(thread_id: str, thread_data: ThreadUpdateRequest):
    """Update thread title"""
    try:
        from services.database import get_database
        
        # Update thread title in MongoDB
        db = await get_database()
        result = await db.threads.update_one(
            {"id": thread_id},
            {
                "$set": {
                    "title": thread_data.title,
                    "updatedAt": datetime.utcnow().isoformat()
                }
            }
        )
        
        if result.matched_count == 0:
            raise HTTPException(status_code=404, detail="Thread not found")
        
        return SuccessResponse(
            ok=True,
            message="Thread updated successfully"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update thread: {str(e)}")

@router.delete("/threads/{thread_id}", response_model=SuccessResponse)
async def delete_thread(thread_id: str):
    """Delete a thread"""
    try:
        from services.database import get_database
        
        # Delete thread and all its messages from MongoDB
        db = await get_database()
        
        # Delete all messages for this thread
        messages_result = await db.messages.delete_many({"threadId": thread_id})
        
        # Delete the thread
        thread_result = await db.threads.delete_one({"id": thread_id})
        
        if thread_result.deleted_count == 0:
            raise HTTPException(status_code=404, detail="Thread not found")
        
        return SuccessResponse(
            ok=True,
            message=f"Thread and {messages_result.deleted_count} messages deleted successfully"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete thread: {str(e)}")

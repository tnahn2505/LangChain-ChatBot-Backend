"""
Pydantic models for request/response validation
Defines all data schemas used in API endpoints
"""
from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field

# =============================================================================
# HEALTH CHECK MODELS
# =============================================================================

class HealthResponse(BaseModel):
    """Health check response model"""
    ok: bool
    message: str
    timestamp: str

# =============================================================================
# THREAD MODELS
# =============================================================================

class ThreadCreate(BaseModel):
    """Create thread request model"""
    title: str = Field(..., min_length=1, max_length=200, description="Thread title")

class ThreadUpdate(BaseModel):
    """Update thread request model"""
    title: str = Field(..., min_length=1, max_length=200, description="New thread title")

class ThreadOut(BaseModel):
    """Thread response model"""
    id: str
    title: str
    updatedAt: str
    createdAt: str
    messagesCount: int = 0

class ThreadListResponse(BaseModel):
    """Thread list response model"""
    threads: List[ThreadOut]
    total: int
    skip: int = 0
    limit: int = 50

# =============================================================================
# MESSAGE MODELS
# =============================================================================

class MessageCreate(BaseModel):
    """Create message request model"""
    content: str = Field(..., min_length=1, max_length=10000, description="Message content")
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Additional metadata")

class MessageOut(BaseModel):
    """Message response model"""
    id: str
    role: str
    content: str
    createdAt: str

class SendMessageRequest(BaseModel):
    """Send message request model"""
    content: str = Field(..., min_length=1, max_length=10000, description="Message content")
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Additional metadata")

class SendMessageResponse(BaseModel):
    """Send message response model"""
    thread_id: str
    user_message_id: str
    assistant_message_id: str
    assistant: Dict[str, Any]

class MessageListResponse(BaseModel):
    """Message list response model"""
    messages: List[MessageOut]
    total: int
    skip: int = 0
    limit: int = 50

# =============================================================================
# SUCCESS RESPONSE MODELS
# =============================================================================

class SuccessResponse(BaseModel):
    """Success response model"""
    ok: bool
    message: Optional[str] = None

class ThreadCreateResponse(BaseModel):
    """Create thread response model"""
    id: str = Field(..., description="Created thread ID")

# =============================================================================
# AI SERVICE MODELS
# =============================================================================

class AIUsage(BaseModel):
    """AI usage statistics model"""
    prompt_tokens: int = 0
    completion_tokens: int = 0
    total_tokens: int = 0

class AIResponse(BaseModel):
    """AI response model"""
    content: str
    model: str
    usage: AIUsage
    latency_ms: int = 0

# =============================================================================
# INTERNAL MODELS (for database operations)
# =============================================================================

class ThreadDocument(BaseModel):
    """Thread document model for database operations"""
    id: str
    title: str
    createdAt: str
    updatedAt: str

class MessageDocument(BaseModel):
    """Message document model for database operations"""
    id: str
    threadId: str
    role: str
    content: str
    createdAt: str
    metadata: Optional[Dict[str, Any]] = None

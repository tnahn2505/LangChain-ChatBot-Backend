"""
Message database model
"""
from pydantic import BaseModel, Field
from typing import Dict, Any, Optional
from datetime import datetime

class Message(BaseModel):
    id: str
    threadId: str
    role: str  # 'user', 'assistant', 'system'
    content: str
    createdAt: str
    metadata: Optional[Dict[str, Any]] = {}

class MessageCreate(BaseModel):
    threadId: str
    role: str
    content: str = Field(..., min_length=1, max_length=10000)
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict)

class MessageResponse(BaseModel):
    id: str
    role: str
    content: str
    createdAt: str

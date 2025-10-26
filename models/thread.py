"""
Thread database model
"""
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime

class Thread(BaseModel):
    id: str
    title: str
    updatedAt: str
    createdAt: str
    messagesCount: int = 0
    archived: bool = False
    tags: List[str] = []

class ThreadCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)

class ThreadUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    archived: Optional[bool] = None
    tags: Optional[List[str]] = None

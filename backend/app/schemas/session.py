from typing import Optional, List, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field

class SessionCreateRequest(BaseModel):
    title: Optional[str] = Field(default="New Conversation", max_length=255)
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict)

class SessionUpdateRequest(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)

class MessageResponse(BaseModel):
    id: str
    session_id: str
    role: str
    content: str
    citations: Optional[List[Dict[str, Any]]] = Field(default_factory=list)
    created_at: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict)

class SessionResponse(BaseModel):
    id: str
    title: str
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
    message_count: int = 0
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict)

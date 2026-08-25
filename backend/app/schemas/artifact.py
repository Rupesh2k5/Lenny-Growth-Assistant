from typing import Optional, Dict, Any
from pydantic import BaseModel, Field

class ArtifactCreateRequest(BaseModel):
    session_id: str
    prompt: str
    artifact_type: Optional[str] = Field(default="html", description="markdown | html")
    provider: Optional[str] = None

class ArtifactResponse(BaseModel):
    id: str
    session_id: str
    message_id: Optional[str] = None
    title: str
    type: str
    content: str
    sanitized_content: Optional[str] = None
    created_at: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict)

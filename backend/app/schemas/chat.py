from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field

class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=20000, description="User question or prompt")
    provider: Optional[str] = Field(default=None, description="Model provider: ollama | anthropic | openai | mock")
    stream: Optional[bool] = Field(default=False, description="Enable SSE token streaming")

class Citation(BaseModel):
    citation_id: str
    source_id: str
    episode_id: str
    speaker: str
    title: str
    url: Optional[str] = None
    relevance_score: float
    passage_quote: str
    content: Optional[str] = None

class ArtifactPreview(BaseModel):
    id: Optional[str] = None
    title: str
    type: str  # 'markdown' | 'html'
    content: str
    sanitized_content: Optional[str] = None

class ChatResponse(BaseModel):
    message_id: str
    session_id: str
    role: str = "assistant"
    content: str
    citations: List[Citation] = Field(default_factory=list)
    intent: str
    provider: str
    model: str
    latency_ms: float
    artifact: Optional[ArtifactPreview] = None
    artifact_id: Optional[str] = None

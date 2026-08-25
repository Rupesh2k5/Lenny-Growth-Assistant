from typing import Optional, List, Dict, Any
from pydantic import BaseModel

class ChunkResponse(BaseModel):
    id: str
    chunk_index: int
    content: str

class SourceResponse(BaseModel):
    id: str
    episode_id: str
    title: str
    speaker: str
    url: Optional[str] = None
    topics: Optional[str] = None
    chunk_count: int = 0
    ingested_at: Optional[str] = None

class SourceDetailResponse(BaseModel):
    id: str
    episode_id: str
    title: str
    speaker: str
    url: Optional[str] = None
    topics: Optional[str] = None
    full_text: str
    chunks: List[ChunkResponse] = []

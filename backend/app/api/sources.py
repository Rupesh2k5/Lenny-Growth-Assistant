from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.database import get_db
from app.repositories.source_repository import SourceRepository
from app.schemas.source import SourceResponse, SourceDetailResponse, ChunkResponse

router = APIRouter(prefix="/sources", tags=["Transcript Sources & Knowledge Base"])

@router.get("", response_model=List[SourceResponse])
async def list_sources(db: AsyncSession = Depends(get_db)):
    """List all indexed podcast episodes in the knowledge base."""
    repo = SourceRepository(db)
    sources = await repo.list_sources()

    return [
        SourceResponse(
            id=s.id,
            episode_id=s.episode_id,
            title=s.title,
            speaker=s.speaker,
            url=s.url,
            topics=s.topics,
            chunk_count=len(s.chunks) if s.chunks else 0,
            ingested_at=s.ingested_at.isoformat() if s.ingested_at else None
        )
        for s in sources
    ]

@router.get("/{source_id}", response_model=SourceDetailResponse)
async def get_source_details(source_id: str, db: AsyncSession = Depends(get_db)):
    """Get full transcript and chunk list for a specific episode."""
    repo = SourceRepository(db)
    source = await repo.get_by_id(source_id)
    if not source:
        raise HTTPException(status_code=404, detail="Source transcript not found")

    return SourceDetailResponse(
        id=source.id,
        episode_id=source.episode_id,
        title=source.title,
        speaker=source.speaker,
        url=source.url,
        topics=source.topics,
        full_text=source.full_text,
        chunks=[
            ChunkResponse(
                id=c.id,
                chunk_index=c.chunk_index,
                content=c.content
            )
            for c in (source.chunks or [])
        ]
    )

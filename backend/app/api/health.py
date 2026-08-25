from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from app.db.database import get_db
from app.db.models import Source, Chunk, Session, Message, Artifact
from app.models.factory import provider_factory
from app.core.config import settings

router = APIRouter(prefix="/health", tags=["Health & Readiness"])

@router.get("")
async def get_system_health(db: AsyncSession = Depends(get_db)):
    """Comprehensive system health and readiness check."""
    # Check DB counts
    try:
        sources_cnt = await db.scalar(select(func.count(Source.id))) or 0
        chunks_cnt = await db.scalar(select(func.count(Chunk.id))) or 0
        sessions_cnt = await db.scalar(select(func.count(Session.id))) or 0
        artifacts_cnt = await db.scalar(select(func.count(Artifact.id))) or 0
        db_status = "connected"
    except Exception as e:
        sources_cnt = chunks_cnt = sessions_cnt = artifacts_cnt = 0
        db_status = f"error: {str(e)}"

    provider_statuses = await provider_factory.get_all_provider_statuses()

    return {
        "status": "healthy" if db_status == "connected" else "degraded",
        "version": settings.VERSION,
        "database": {
            "status": db_status,
            "sources_indexed": sources_cnt,
            "chunks_indexed": chunks_cnt,
            "total_sessions": sessions_cnt,
            "total_artifacts": artifacts_cnt
        },
        "llm": provider_statuses
    }

@router.get("/llm")
async def get_llm_status():
    """Returns status and model details for all configured LLM providers."""
    return await provider_factory.get_all_provider_statuses()

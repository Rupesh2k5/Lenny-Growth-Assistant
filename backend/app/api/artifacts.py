from typing import List
from fastapi import APIRouter, Depends
from fastapi.responses import HTMLResponse, PlainTextResponse
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.database import get_db
from app.services.artifact_service import ArtifactService
from app.schemas.artifact import ArtifactResponse

router = APIRouter(prefix="/artifacts", tags=["Artifact Management & Isolation"])

@router.get("/{artifact_id}", response_model=ArtifactResponse)
async def get_artifact(artifact_id: str, db: AsyncSession = Depends(get_db)):
    """Retrieve artifact details by ID with sanitized content."""
    service = ArtifactService(db)
    return await service.get_artifact(artifact_id)

@router.get("/session/{session_id}", response_model=List[ArtifactResponse])
async def list_session_artifacts(session_id: str, db: AsyncSession = Depends(get_db)):
    """List all artifacts created in a specific session."""
    service = ArtifactService(db)
    return await service.list_artifacts_by_session(session_id)

@router.get("/{artifact_id}/raw")
async def get_raw_artifact_view(artifact_id: str, db: AsyncSession = Depends(get_db)):
    """
    Returns raw sanitized HTML or Markdown with proper Content-Type
    for direct sandboxed iframe loading.
    """
    service = ArtifactService(db)
    art = await service.get_artifact(artifact_id)

    if art.type == "html":
        return HTMLResponse(content=art.sanitized_content or art.content)
    else:
        return PlainTextResponse(content=art.content)

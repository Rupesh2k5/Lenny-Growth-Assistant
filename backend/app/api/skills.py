from typing import Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.db.database import get_db
from app.db.models import Session, Artifact
from app.models.factory import provider_factory
from app.retrieval.retriever import retriever
from app.agents.ship30 import Ship30Skill
from app.agents.artifact_builder import ArtifactBuilderSkill

router = APIRouter(prefix="/skills", tags=["Dedicated Agent Skills"])

class Ship30Request(BaseModel):
    session_id: str
    topic: str
    target_length: Optional[int] = 1250
    provider: Optional[str] = None

class ArtifactSkillRequest(BaseModel):
    session_id: str
    prompt: str
    artifact_type: Optional[str] = "html" # 'html' | 'markdown'
    provider: Optional[str] = None

@router.post("/ship30")
async def generate_ship30_essay(body: Ship30Request, db: AsyncSession = Depends(get_db)):
    """
    Dedicated endpoint for the Ship 30 for 30 essay generation skill.
    Retrieves grounded knowledge and synthesizes a structured ~1,250 word digital essay.
    """
    session_res = await db.execute(select(Session).where(Session.id == body.session_id))
    session = session_res.scalar_one_or_none()
    if not session:
        session = Session(id=body.session_id, title=f"Essay: {body.topic[:30]}")
        db.add(session)
        await db.commit()

    provider = provider_factory.get_provider(body.provider)
    retrieved = await retriever.retrieve_relevant_chunks(body.topic, db)
    retrieval_context = retriever.format_retrieval_context(retrieved)

    skill = Ship30Skill(provider)
    result = await skill.generate_essay(
        topic=body.topic,
        retrieval_context=retrieval_context,
        target_length=body.target_length or 1250
    )

    # Save to artifacts table
    artifact = Artifact(
        session_id=session.id,
        title=result["title"],
        artifact_type="markdown",
        content=result["content"],
        sanitized_content=result["content"],
        artifact_metadata={"skill": "ship30", "word_count": result["word_count"]}
    )
    db.add(artifact)
    await db.commit()
    await db.refresh(artifact)

    return {
        "artifact_id": artifact.id,
        "session_id": session.id,
        "title": artifact.title,
        "content": artifact.content,
        "word_count": result["word_count"],
        "model": result["model"],
        "provider": result["provider"]
    }

@router.post("/artifact")
async def generate_custom_artifact(body: ArtifactSkillRequest, db: AsyncSession = Depends(get_db)):
    """
    Dedicated endpoint for generating custom interactive HTML/CSS widgets or Markdown strategy templates.
    """
    session_res = await db.execute(select(Session).where(Session.id == body.session_id))
    session = session_res.scalar_one_or_none()
    if not session:
        session = Session(id=body.session_id, title="Growth Artifact")
        db.add(session)
        await db.commit()

    provider = provider_factory.get_provider(body.provider)
    retrieved = await retriever.retrieve_relevant_chunks(body.prompt, db)
    retrieval_context = retriever.format_retrieval_context(retrieved)

    builder = ArtifactBuilderSkill(provider)
    result = await builder.generate_artifact(
        prompt=body.prompt,
        artifact_type=body.artifact_type or "html",
        retrieval_context=retrieval_context
    )

    artifact = Artifact(
        session_id=session.id,
        title=result["title"],
        artifact_type=result["type"],
        content=result["content"],
        sanitized_content=result["sanitized_content"],
        artifact_metadata={"skill": "artifact_builder", "requested_format": body.artifact_type}
    )
    db.add(artifact)
    await db.commit()
    await db.refresh(artifact)

    return {
        "artifact_id": artifact.id,
        "session_id": session.id,
        "title": artifact.title,
        "type": artifact.artifact_type,
        "content": artifact.content,
        "sanitized_content": artifact.sanitized_content,
        "model": result["model"],
        "provider": result["provider"]
    }

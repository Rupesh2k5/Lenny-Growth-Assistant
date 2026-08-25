from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories.artifact_repository import ArtifactRepository
from app.repositories.session_repository import SessionRepository
from app.schemas.artifact import ArtifactResponse
from app.core.errors import ResourceNotFoundError
from app.core.security import sanitize_html

class ArtifactService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.artifact_repo = ArtifactRepository(db)
        self.session_repo = SessionRepository(db)

    async def get_artifact(self, artifact_id: str) -> ArtifactResponse:
        artifact = await self.artifact_repo.get_by_id(artifact_id)
        if not artifact:
            raise ResourceNotFoundError(f"Artifact '{artifact_id}' not found.")
        
        sanitized = sanitize_html(artifact.content) if artifact.type == "html" else artifact.content
        return ArtifactResponse(
            id=artifact.id,
            session_id=artifact.session_id,
            message_id=artifact.message_id,
            title=artifact.title,
            type=artifact.type,
            content=artifact.content,
            sanitized_content=sanitized,
            created_at=artifact.created_at.isoformat() if artifact.created_at else None,
            metadata=artifact.artifact_metadata or {}
        )

    async def list_artifacts_by_session(self, session_id: str) -> List[ArtifactResponse]:
        artifacts = await self.artifact_repo.list_by_session(session_id)
        return [
            ArtifactResponse(
                id=a.id,
                session_id=a.session_id,
                message_id=a.message_id,
                title=a.title,
                type=a.type,
                content=a.content,
                sanitized_content=sanitize_html(a.content) if a.type == "html" else a.content,
                created_at=a.created_at.isoformat() if a.created_at else None,
                metadata=a.artifact_metadata or {}
            )
            for a in artifacts
        ]

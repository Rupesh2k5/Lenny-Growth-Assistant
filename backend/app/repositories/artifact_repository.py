import uuid
from typing import List, Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from app.db.models import Artifact
from app.core.errors import ResourceNotFoundError

class ArtifactRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(
        self,
        session_id: str,
        title: str,
        type: str,
        content: str,
        message_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
        artifact_id: Optional[str] = None
    ) -> Artifact:
        art_id = artifact_id or str(uuid.uuid4())
        artifact = Artifact(
            id=art_id,
            session_id=session_id,
            message_id=message_id,
            title=title,
            artifact_type=type,
            content=content,
            artifact_metadata=metadata or {}
        )
        self.db.add(artifact)
        await self.db.flush()
        return artifact

    async def get_by_id(self, artifact_id: str) -> Optional[Artifact]:
        stmt = select(Artifact).where(Artifact.id == artifact_id)
        res = await self.db.execute(stmt)
        return res.scalar_one_or_none()

    async def list_by_session(self, session_id: str) -> List[Artifact]:
        stmt = select(Artifact).where(Artifact.session_id == session_id).order_by(desc(Artifact.created_at))
        res = await self.db.execute(stmt)
        return list(res.scalars().all())

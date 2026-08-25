import uuid
from typing import List, Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete, desc
from sqlalchemy.orm import selectinload
from app.db.models import Session
from app.core.errors import ResourceNotFoundError

class SessionRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, title: str = "New Conversation", metadata: Optional[Dict[str, Any]] = None) -> Session:
        session_id = str(uuid.uuid4())
        session = Session(
            id=session_id,
            title=title,
            session_metadata=metadata or {}
        )
        self.db.add(session)
        await self.db.flush()
        return session

    async def get_by_id(self, session_id: str) -> Optional[Session]:
        stmt = select(Session).where(Session.id == session_id)
        res = await self.db.execute(stmt)
        return res.scalar_one_or_none()

    async def get_or_create(self, session_id: str, default_title: str = "New Conversation") -> Session:
        existing = await self.get_by_id(session_id)
        if existing:
            return existing
        session = Session(id=session_id, title=default_title, session_metadata={})
        self.db.add(session)
        await self.db.flush()
        return session

    async def list_all(self, limit: int = 50) -> List[Session]:
        # Eagerly load messages to avoid MissingGreenlet errors
        stmt = select(Session).options(selectinload(Session.messages)).order_by(desc(Session.updated_at)).limit(limit)
        res = await self.db.execute(stmt)
        return list(res.scalars().all())

    async def update_title(self, session_id: str, title: str) -> Session:
        session = await self.get_by_id(session_id)
        if not session:
            raise ResourceNotFoundError(f"Session with ID '{session_id}' not found.")
        session.title = title
        await self.db.flush()
        return session

    async def delete(self, session_id: str) -> bool:
        session = await self.get_by_id(session_id)
        if not session:
            raise ResourceNotFoundError(f"Session with ID '{session_id}' not found.")
        await self.db.delete(session)
        await self.db.flush()
        return True

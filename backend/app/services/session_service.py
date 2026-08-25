import uuid
from typing import List, Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories.session_repository import SessionRepository
from app.repositories.message_repository import MessageRepository
from app.schemas.session import SessionResponse, MessageResponse
from app.core.errors import ResourceNotFoundError

class SessionService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.session_repo = SessionRepository(db)
        self.message_repo = MessageRepository(db)

    async def create_session(self, title: str = "New Conversation", metadata: Optional[Dict[str, Any]] = None) -> SessionResponse:
        session = await self.session_repo.create(title=title, metadata=metadata)
        await self.db.commit()
        return SessionResponse(
            id=session.id,
            title=session.title,
            created_at=session.created_at.isoformat() if session.created_at else None,
            updated_at=session.updated_at.isoformat() if session.updated_at else None,
            message_count=0,
            metadata=session.session_metadata
        )

    async def get_session(self, session_id: str) -> SessionResponse:
        session = await self.session_repo.get_by_id(session_id)
        if not session:
            raise ResourceNotFoundError(f"Session '{session_id}' not found.")
        messages = await self.message_repo.list_by_session(session_id)
        return SessionResponse(
            id=session.id,
            title=session.title,
            created_at=session.created_at.isoformat() if session.created_at else None,
            updated_at=session.updated_at.isoformat() if session.updated_at else None,
            message_count=len(messages),
            metadata=session.session_metadata
        )

    async def list_sessions(self, limit: int = 50) -> List[SessionResponse]:
        sessions = await self.session_repo.list_all(limit=limit)
        results = []
        for s in sessions:
            results.append(SessionResponse(
                id=s.id,
                title=s.title,
                created_at=s.created_at.isoformat() if s.created_at else None,
                updated_at=s.updated_at.isoformat() if s.updated_at else None,
                message_count=len(s.messages) if s.messages else 0,
                metadata=s.session_metadata
            ))
        return results

    async def list_messages(self, session_id: str) -> List[MessageResponse]:
        session = await self.session_repo.get_by_id(session_id)
        if not session:
            raise ResourceNotFoundError(f"Session '{session_id}' not found.")
        messages = await self.message_repo.list_by_session(session_id)
        return [
            MessageResponse(
                id=m.id,
                session_id=m.session_id,
                role=m.role,
                content=m.content,
                citations=m.citations or [],
                created_at=m.created_at.isoformat() if m.created_at else None,
                metadata=m.message_metadata or {}
            )
            for m in messages
        ]

    async def update_session_title(self, session_id: str, title: str) -> SessionResponse:
        session = await self.session_repo.update_title(session_id, title)
        await self.db.commit()
        return SessionResponse(
            id=session.id,
            title=session.title,
            created_at=session.created_at.isoformat() if session.created_at else None,
            updated_at=session.updated_at.isoformat() if session.updated_at else None,
            message_count=0,
            metadata=session.session_metadata
        )

    async def delete_session(self, session_id: str) -> bool:
        res = await self.session_repo.delete(session_id)
        await self.db.commit()
        return res

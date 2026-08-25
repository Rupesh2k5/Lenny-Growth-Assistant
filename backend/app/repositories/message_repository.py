import uuid
from typing import List, Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, asc
from app.db.models import Message

class MessageRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(
        self,
        session_id: str,
        role: str,
        content: str,
        citations: Optional[List[Dict[str, Any]]] = None,
        metadata: Optional[Dict[str, Any]] = None,
        message_id: Optional[str] = None
    ) -> Message:
        msg_id = message_id or str(uuid.uuid4())
        msg = Message(
            id=msg_id,
            session_id=session_id,
            role=role,
            content=content,
            citations=citations or [],
            message_metadata=metadata or {}
        )
        self.db.add(msg)
        await self.db.flush()
        return msg

    async def list_by_session(self, session_id: str) -> List[Message]:
        stmt = select(Message).where(Message.session_id == session_id).order_by(asc(Message.created_at))
        res = await self.db.execute(stmt)
        return list(res.scalars().all())

    async def get_history_dicts(self, session_id: str, limit: int = 10) -> List[Dict[str, str]]:
        messages = await self.list_by_session(session_id)
        return [{"role": m.role, "content": m.content} for m in messages[-limit:]]

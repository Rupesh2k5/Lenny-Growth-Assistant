from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from sqlalchemy.orm import selectinload
from app.db.models import Source, Chunk

class SourceRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def list_sources(self) -> List[Source]:
        stmt = select(Source).options(selectinload(Source.chunks)).order_by(Source.title)
        res = await self.db.execute(stmt)
        return list(res.scalars().all())

    async def get_by_id(self, source_id: str) -> Optional[Source]:
        stmt = select(Source).options(selectinload(Source.chunks)).where(Source.id == source_id)
        res = await self.db.execute(stmt)
        return res.scalar_one_or_none()

    async def get_by_episode_id(self, episode_id: str) -> Optional[Source]:
        stmt = select(Source).options(selectinload(Source.chunks)).where(Source.episode_id == episode_id)
        res = await self.db.execute(stmt)
        return res.scalar_one_or_none()

    async def count_sources(self) -> int:
        stmt = select(func.count(Source.id))
        res = await self.db.execute(stmt)
        return res.scalar() or 0

    async def count_chunks(self) -> int:
        stmt = select(func.count(Chunk.id))
        res = await self.db.execute(stmt)
        return res.scalar() or 0

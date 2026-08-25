from typing import List
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.database import get_db
from app.services.session_service import SessionService
from app.schemas.session import (
    SessionCreateRequest,
    SessionUpdateRequest,
    SessionResponse,
    MessageResponse
)

router = APIRouter(prefix="/sessions", tags=["Session Persistence"])

@router.get("", response_model=List[SessionResponse])
async def list_sessions(db: AsyncSession = Depends(get_db)):
    """List all user sessions ordered by last update."""
    service = SessionService(db)
    return await service.list_sessions()

@router.post("", response_model=SessionResponse, status_code=status.HTTP_201_CREATED)
async def create_session(body: SessionCreateRequest, db: AsyncSession = Depends(get_db)):
    """Create a new conversational session."""
    service = SessionService(db)
    return await service.create_session(title=body.title or "New Conversation", metadata=body.metadata)

@router.get("/{session_id}/messages", response_model=List[MessageResponse])
async def get_session_messages(session_id: str, db: AsyncSession = Depends(get_db)):
    """Get all messages for a specific session."""
    service = SessionService(db)
    return await service.list_messages(session_id)

@router.patch("/{session_id}", response_model=SessionResponse)
async def update_session_title(session_id: str, body: SessionUpdateRequest, db: AsyncSession = Depends(get_db)):
    """Update session title."""
    service = SessionService(db)
    return await service.update_session_title(session_id, body.title)

@router.delete("/{session_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_session(session_id: str, db: AsyncSession = Depends(get_db)):
    """Delete a session and all its messages and artifacts."""
    service = SessionService(db)
    await service.delete_session(session_id)
    return None

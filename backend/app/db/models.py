import uuid
from datetime import datetime
from typing import Optional, List
from sqlalchemy import Column, String, Text, DateTime, ForeignKey, Integer, Float, JSON
from sqlalchemy.orm import relationship
from app.db.database import Base

def generate_uuid():
    return str(uuid.uuid4())

class Session(Base):
    __tablename__ = "sessions"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    title = Column(String(255), nullable=False, default="New Conversation")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    session_metadata = Column(JSON, default=dict)

    # Relationships
    messages = relationship("Message", back_populates="session", cascade="all, delete-orphan", order_by="Message.created_at")
    artifacts = relationship("Artifact", back_populates="session", cascade="all, delete-orphan", order_by="Artifact.created_at")

class Message(Base):
    __tablename__ = "messages"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    session_id = Column(String(36), ForeignKey("sessions.id", ondelete="CASCADE"), nullable=False)
    role = Column(String(20), nullable=False)  # 'user' | 'assistant' | 'system'
    content = Column(Text, nullable=False)
    citations = Column(JSON, default=list)  # [{citation_id, source_id, speaker, episode_id, quote, relevance}]
    created_at = Column(DateTime, default=datetime.utcnow)
    message_metadata = Column(JSON, default=dict)  # {model, latency_ms, intent}

    # Relationships
    session = relationship("Session", back_populates="messages")
    artifacts = relationship("Artifact", back_populates="message")

class Artifact(Base):
    __tablename__ = "artifacts"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    session_id = Column(String(36), ForeignKey("sessions.id", ondelete="CASCADE"), nullable=False)
    message_id = Column(String(36), ForeignKey("messages.id", ondelete="SET NULL"), nullable=True)
    title = Column(String(255), nullable=False)
    artifact_type = Column(String(20), nullable=False)  # 'markdown' | 'html'
    content = Column(Text, nullable=False)
    sanitized_content = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    artifact_metadata = Column(JSON, default=dict)  # {skill: 'ship30', word_count: 1250}

    # Relationships
    session = relationship("Session", back_populates="artifacts")
    message = relationship("Message", back_populates="artifacts")

    @property
    def type(self) -> str:
        return self.artifact_type

class Source(Base):
    __tablename__ = "sources"

    id = Column(String(50), primary_key=True)  # EP-101 etc
    episode_id = Column(String(50), nullable=False)
    title = Column(String(255), nullable=False)
    speaker = Column(String(255), nullable=False)
    url = Column(String(500), nullable=True)
    topics = Column(String(500), nullable=True)
    full_text = Column(Text, nullable=False)
    ingested_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    chunks = relationship("Chunk", back_populates="source", cascade="all, delete-orphan")

class Chunk(Base):
    __tablename__ = "chunks"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    source_id = Column(String(50), ForeignKey("sources.id", ondelete="CASCADE"), nullable=False)
    chunk_index = Column(Integer, nullable=False)
    content = Column(Text, nullable=False)
    embedding = Column(JSON, nullable=True)  # vector representation
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    source = relationship("Source", back_populates="chunks")

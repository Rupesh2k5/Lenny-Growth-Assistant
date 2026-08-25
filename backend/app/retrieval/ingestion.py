import os
import re
import glob
from typing import List, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from app.db.models import Source, Chunk
from app.retrieval.embeddings import embedding_engine
from app.core.config import settings
from app.core.logging import logger

class TranscriptIngestionService:
    def __init__(self, transcripts_dir: str = settings.TRANSCRIPTS_DIR):
        self.transcripts_dir = transcripts_dir

    def parse_markdown_transcript(self, file_path: str) -> Dict[str, Any]:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()

        # Extract metadata from top header
        title_match = re.search(r"^#\s+(.+)$", content, re.MULTILINE)
        guest_match = re.search(r"\*\*Guest\*\*:\s*([^\n]+)", content)
        ep_id_match = re.search(r"\*\*Episode ID\*\*:\s*([^\n]+)", content)
        url_match = re.search(r"\*\*URL\*\*:\s*([^\n]+)", content)
        topics_match = re.search(r"\*\*Topics\*\*:\s*([^\n]+)", content)

        title = title_match.group(1).strip() if title_match else os.path.basename(file_path)
        guest = guest_match.group(1).strip() if guest_match else "Lenny's Guest"
        episode_id = ep_id_match.group(1).strip() if ep_id_match else os.path.splitext(os.path.basename(file_path))[0]
        url = url_match.group(1).strip() if url_match else ""
        topics = topics_match.group(1).strip() if topics_match else "Product, Growth"

        return {
            "id": episode_id,
            "episode_id": episode_id,
            "title": title,
            "speaker": guest,
            "url": url,
            "topics": topics,
            "full_text": content
        }

    def chunk_transcript(self, source_dict: Dict[str, Any], chunk_size: int = settings.CHUNK_SIZE) -> List[Dict[str, Any]]:
        text = source_dict["full_text"]
        # Split on headers (### On ...) or double newlines
        sections = re.split(r'(?=###\s+)', text)
        chunks = []
        chunk_idx = 0

        for section in sections:
            section = section.strip()
            if not section:
                continue

            words = section.split()
            if len(words) <= chunk_size:
                embedding = embedding_engine.compute_dense_vector(section)
                chunks.append({
                    "source_id": source_dict["id"],
                    "chunk_index": chunk_idx,
                    "content": section,
                    "embedding": embedding
                })
                chunk_idx += 1
            else:
                # Sub-chunk large sections with overlap
                for i in range(0, len(words), chunk_size - settings.CHUNK_OVERLAP):
                    sub_text = " ".join(words[i:i + chunk_size])
                    embedding = embedding_engine.compute_dense_vector(sub_text)
                    chunks.append({
                        "source_id": source_dict["id"],
                        "chunk_index": chunk_idx,
                        "content": sub_text,
                        "embedding": embedding
                    })
                    chunk_idx += 1

        return chunks

    async def ingest_all_transcripts(self, db_session: AsyncSession) -> Dict[str, Any]:
        """Loads and indexes all markdown transcripts into database."""
        # Find transcript files
        search_paths = [
            os.path.join(self.transcripts_dir, "*.md"),
            os.path.join(os.path.dirname(os.path.abspath(__file__)), "../../../data/transcripts/*.md"),
            "data/transcripts/*.md",
            "../data/transcripts/*.md"
        ]
        
        files = []
        for p in search_paths:
            found = glob.glob(p)
            if found:
                files = found
                break

        if not files:
            logger.warning(f"No transcript files found in search paths: {search_paths}")
            return {"ingested_sources": 0, "ingested_chunks": 0}

        ingested_sources = 0
        ingested_chunks = 0

        for fpath in files:
            source_data = self.parse_markdown_transcript(fpath)
            
            # Check existing source
            existing = await db_session.execute(select(Source).where(Source.id == source_data["id"]))
            existing_source = existing.scalar_one_or_none()

            if existing_source:
                # Update existing
                existing_source.title = source_data["title"]
                existing_source.speaker = source_data["speaker"]
                existing_source.url = source_data["url"]
                existing_source.topics = source_data["topics"]
                existing_source.full_text = source_data["full_text"]
                # Clear old chunks
                await db_session.execute(delete(Chunk).where(Chunk.source_id == source_data["id"]))
            else:
                new_source = Source(
                    id=source_data["id"],
                    episode_id=source_data["episode_id"],
                    title=source_data["title"],
                    speaker=source_data["speaker"],
                    url=source_data["url"],
                    topics=source_data["topics"],
                    full_text=source_data["full_text"]
                )
                db_session.add(new_source)

            # Generate and add chunks
            chunks_data = self.chunk_transcript(source_data)
            for c in chunks_data:
                chunk = Chunk(
                    source_id=c["source_id"],
                    chunk_index=c["chunk_index"],
                    content=c["content"],
                    embedding=c["embedding"]
                )
                db_session.add(chunk)
                ingested_chunks += 1

            ingested_sources += 1

        await db_session.commit()
        logger.info(f"Ingested {ingested_sources} sources and {ingested_chunks} chunks.")
        return {"ingested_sources": ingested_sources, "ingested_chunks": ingested_chunks}

ingestion_service = TranscriptIngestionService()

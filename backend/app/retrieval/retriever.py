from typing import List, Dict, Any, Optional
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.db.models import Source, Chunk
from app.retrieval.embeddings import embedding_engine
from app.core.config import settings
from app.core.logging import logger

class RetrievedCitation(BaseModel):
    citation_id: str          # e.g. "S1", "S2"
    source_id: str            # e.g. "EP-101"
    episode_id: str
    speaker: str
    title: str
    url: str
    content: str
    relevance_score: float
    passage_quote: str

class TranscriptRetriever:
    async def retrieve_relevant_chunks(
        self,
        query: str,
        db_session: AsyncSession,
        top_k: int = settings.MAX_RETRIEVAL_CHUNKS,
        threshold: float = settings.SIMILARITY_THRESHOLD
    ) -> List[RetrievedCitation]:
        """
        Retrieves top-K most relevant transcript passages for a given query.
        Calculates cosine similarity between query vector and chunk embeddings.
        """
        query_vec = embedding_engine.compute_dense_vector(query)
        
        # Fetch all chunks and sources
        stmt = select(Chunk, Source).join(Source, Chunk.source_id == Source.id)
        result = await db_session.execute(stmt)
        rows = result.all()

        scored_results = []
        for chunk, source in rows:
            chunk_vec = chunk.embedding or []
            score = embedding_engine.cosine_similarity(query_vec, chunk_vec)
            
            # Boost score if query keywords appear directly in speaker or topics
            q_lower = query.lower()
            if source.speaker.lower() in q_lower or source.title.lower() in q_lower:
                score += 0.25
            
            # Check key topic matches
            for word in q_lower.split():
                if len(word) > 3 and word in chunk.content.lower():
                    score += 0.05

            score = min(1.0, score)

            if score >= threshold:
                # Extract clean representative quote
                clean_lines = [l.strip() for l in chunk.content.split("\n") if l.strip() and not l.startswith("#")]
                passage_quote = clean_lines[0][:200] + "..." if clean_lines else chunk.content[:200] + "..."

                scored_results.append({
                    "chunk": chunk,
                    "source": source,
                    "score": round(score, 4),
                    "passage_quote": passage_quote
                })

        # Sort descending by score
        scored_results.sort(key=lambda x: x["score"], reverse=True)
        top_matches = scored_results[:top_k]

        citations: List[RetrievedCitation] = []
        for idx, match in enumerate(top_matches, start=1):
            src = match["source"]
            chk = match["chunk"]
            citations.append(
                RetrievedCitation(
                    citation_id=f"S{idx}",
                    source_id=src.id,
                    episode_id=src.episode_id,
                    speaker=src.speaker,
                    title=src.title,
                    url=src.url or "",
                    content=chk.content,
                    relevance_score=match["score"],
                    passage_quote=match["passage_quote"]
                )
            )

        logger.info(f"Retrieval query='{query}' -> {len(citations)} chunks matched (top score: {citations[0].relevance_score if citations else 0.0})")
        return citations

    def format_retrieval_context(self, citations: List[RetrievedCitation]) -> str:
        """Formats citations into a clean, numbered context block for LLM prompt."""
        if not citations:
            return "NO RELEVANT EVIDENCE FOUND IN TRANSCRIPTS."

        context_blocks = []
        for cit in citations:
            block = (
                f"SOURCE [{cit.citation_id}]\n"
                f"Speaker/Guest: {cit.speaker}\n"
                f"Episode: {cit.title} (ID: {cit.episode_id})\n"
                f"Relevant Passage:\n{cit.content}\n"
            )
            context_blocks.append(block)

        return "\n---\n".join(context_blocks)

retriever = TranscriptRetriever()

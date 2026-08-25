import re
from typing import List, Dict, Any, Set
from app.retrieval.retriever import RetrievedCitation

class CitationValidator:
    """
    Validates, extracts, and matches inline citation tags [S1], [S2] in generated responses.
    """
    CITATION_PATTERN = re.compile(r'\[S(\d+)\]')

    def extract_cited_sources(
        self,
        text: str,
        available_citations: List[RetrievedCitation]
    ) -> List[Dict[str, Any]]:
        """
        Scans text for [S1], [S2] tokens and returns matched citation metadata.
        """
        cit_map = {cit.citation_id: cit for cit in available_citations}
        matches = self.CITATION_PATTERN.findall(text)
        
        cited_keys: Set[str] = {f"S{m}" for m in matches}
        cited_sources: List[Dict[str, Any]] = []

        # If LLM cited specific tokens, filter to those; otherwise if response is grounded and citations available, include top matching
        for key in sorted(cited_keys, key=lambda x: int(x[1:])):
            if key in cit_map:
                cit = cit_map[key]
                cited_sources.append({
                    "citation_id": cit.citation_id,
                    "source_id": cit.source_id,
                    "episode_id": cit.episode_id,
                    "speaker": cit.speaker,
                    "title": cit.title,
                    "url": cit.url,
                    "relevance_score": cit.relevance_score,
                    "passage_quote": cit.passage_quote,
                    "content": cit.content
                })

        # Fallback: If no explicit [S#] tag was parsed but relevant citations were provided in context, attach top citations
        if not cited_sources and available_citations and "couldn't find" not in text.lower():
            for cit in available_citations[:2]:
                cited_sources.append({
                    "citation_id": cit.citation_id,
                    "source_id": cit.source_id,
                    "episode_id": cit.episode_id,
                    "speaker": cit.speaker,
                    "title": cit.title,
                    "url": cit.url,
                    "relevance_score": cit.relevance_score,
                    "passage_quote": cit.passage_quote,
                    "content": cit.content
                })

        return cited_sources

citation_validator = CitationValidator()

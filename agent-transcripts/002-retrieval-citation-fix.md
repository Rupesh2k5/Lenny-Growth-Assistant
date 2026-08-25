# Agent Transcript 002: Retrieval Grounding & Citation Traceability Hardening

**Timestamp**: 2026-08-24T10:45:00Z  
**Agent Role**: Forward Deployed Engineer Assistant  
**Topic**: Solving Citation Hallucination & Ensuring Deterministic Passage Attribution

---

## 1. Problem Identified
During early retrieval testing, LLMs sometimes fabricated citation markers like `[Episode 45]` or cited a guest who wasn't in the retrieved passage context.

## 2. Root Cause Analysis
- Context injection was formatting passages loosely without a strict indexing schema.
- The prompt lacked an unambiguous citation token mapping protocol.

## 3. Resolution & Engineering Implementation
1. **Standardized Chunk Indexing**:
   - In `backend/app/retrieval/retriever.py`, retrieved chunks are normalized into indexed slots `[S1]`, `[S2]`, `[S3]`, `[S4]`.
   - Each slot is explicitly tagged with `Source ID`, `Guest`, `Episode Title`, `Relevance Score`, and `Passage Quote`.
2. **Strict System Prompt Constraints**:
   - System prompt instructs: *"You MUST ONLY cite passages using `[S1]`, `[S2]`. If a statement is not supported by the retrieved passages, do NOT include a citation. If the entire query has no supporting passage, declare that the knowledge base has no evidence."*
3. **Post-Processing Citation Extraction**:
   - `backend/app/retrieval/citations.py` parses `[S#]` tags in the response and associates them with the full metadata object so the frontend can render rich, interactive source cards.

## 4. Verification
- Tested with query *"How should a startup decide what NOT to build?"* $\to$ Correctly citations `[S1] Brian Chesky (Airbnb EP-101)`.
- Tested with query *"Quantum computing"* $\to$ Correctly triggered unsupported-query refusal with $0$ citations and suggested topics.

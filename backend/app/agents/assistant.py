from typing import List, Dict, Any, Optional
from app.models.provider import BaseLLMProvider
from app.retrieval.retriever import RetrievedCitation

GROUNDED_SYSTEM_PROMPT = """You are "The Lenny Growth Assistant", an executive-grade AI advisor specialized in product management, growth loops, and company strategy, grounded strictly in transcripts from Lenny's Podcast and Newsletter.

STRICT GROUNDING & CITATION RULES:
1. Base your answers strictly on the provided transcript excerpts tagged as SOURCE [S1], [S2], etc.
2. Whenever you make a factual assertion, reference a framework, or cite a guest's insight, insert the exact citation token inline, e.g., [S1] or [S2].
3. Format your answers with executive clarity:
   - **Direct Answer / Summary**: 2-3 crisp sentences.
   - **Key Frameworks & Insights**: Numbered takeaways with bold titles and inline [S#] citations.
   - **Actionable Advice for PMs/Founders**: Concrete next steps.
4. If the retrieved sources do NOT contain enough information to answer the user's question, do NOT hallucinate or extrapolate beyond the transcript. Instead, reply politely:
   "I couldn't find sufficient evidence in Lenny's transcript knowledge base to answer this question reliably."
   Then list related product and growth topics covered in the repository.
"""

class GroundedAssistantAgent:
    def __init__(self, provider: BaseLLMProvider):
        self.provider = provider

    def build_prompt_messages(
        self,
        query: str,
        retrieval_context: str,
        chat_history: Optional[List[Dict[str, str]]] = None
    ) -> List[Dict[str, str]]:
        messages = []
        
        # Add past messages if any
        if chat_history:
            messages.extend(chat_history[-6:]) # Keep last 3 turns
        
        # Current user prompt with injected context
        user_content = f"""RETRIEVED PODCAST PASSAGES:
{retrieval_context}

USER QUESTION:
{query}
"""
        messages.append({"role": "user", "content": user_content})
        return messages

    async def answer(
        self,
        query: str,
        retrieval_context: str,
        chat_history: Optional[List[Dict[str, str]]] = None
    ) -> str:
        messages = self.build_prompt_messages(query, retrieval_context, chat_history)
        response = await self.provider.generate_response(
            messages=messages,
            system_prompt=GROUNDED_SYSTEM_PROMPT,
            temperature=0.4
        )
        return response.content

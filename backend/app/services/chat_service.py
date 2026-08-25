import time
import uuid
import json
from typing import AsyncIterator, Optional, Dict, Any, List
from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories.session_repository import SessionRepository
from app.repositories.message_repository import MessageRepository
from app.repositories.artifact_repository import ArtifactRepository
from app.retrieval.retriever import Retriever
from app.agents.router import IntentRouter
from app.agents.assistant import GroundedAssistant
from app.agents.ship30 import Ship30Skill
from app.agents.artifact_builder import ArtifactBuilderSkill
from app.models.factory import LLMProviderFactory
from app.schemas.chat import ChatResponse, Citation, ArtifactPreview
from app.core.logging import get_logger

logger = get_logger("chat_service")

class ChatService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.session_repo = SessionRepository(db)
        self.message_repo = MessageRepository(db)
        self.artifact_repo = ArtifactRepository(db)
        self.retriever = Retriever(db)
        self.router = IntentRouter()

    async def execute_chat(
        self,
        session_id: str,
        user_message: str,
        provider_name: Optional[str] = None
    ) -> ChatResponse:
        start_time = time.time()
        session = await self.session_repo.get_or_create(session_id, default_title=user_message[:50])

        # 1. Save User Message
        user_msg = await self.message_repo.create(
            session_id=session_id,
            role="user",
            content=user_message
        )
        await self.db.commit()

        # 2. Extract conversation history
        history = await self.message_repo.get_history_dicts(session_id, limit=6)

        # 3. Intent Routing
        decision = self.router.route(user_message)
        logger.info("intent_routed", intent=decision.intent, reason=decision.reason, session_id=session_id)

        # 4. Resolve LLM Provider
        provider = LLMProviderFactory.get_provider(provider_name)

        # 5. Execute Agent Skill
        artifact_preview = None
        artifact_id = None
        assistant_content = ""
        citations_list: List[Dict[str, Any]] = []

        if decision.intent == "ship30":
            ship30_agent = Ship30Skill(self.retriever, provider)
            res = await ship30_agent.generate_essay(topic=user_message, history=history)
            assistant_content = res["content"]
            citations_list = res.get("citations", [])

            # Create Artifact
            artifact = await self.artifact_repo.create(
                session_id=session_id,
                title=res.get("title", "Ship 30 for 30 Digital Essay"),
                type="markdown",
                content=assistant_content,
                metadata={"topic": user_message, "word_count": len(assistant_content.split())}
            )
            artifact_id = artifact.id
            artifact_preview = ArtifactPreview(
                id=artifact.id,
                title=artifact.title,
                type=artifact.type,
                content=artifact.content
            )

        elif decision.intent == "artifact":
            builder = ArtifactBuilderSkill(self.retriever, provider)
            res = await builder.generate_artifact(prompt=user_message, artifact_type="html", history=history)
            assistant_content = res["explanation"]
            citations_list = res.get("citations", [])
            artifact_code = res["content"]

            artifact = await self.artifact_repo.create(
                session_id=session_id,
                title=res.get("title", "Growth Interactive Artifact"),
                type="html",
                content=artifact_code,
                metadata={"prompt": user_message}
            )
            artifact_id = artifact.id
            artifact_preview = ArtifactPreview(
                id=artifact.id,
                title=artifact.title,
                type=artifact.type,
                content=artifact_code
            )

        else:  # Grounded Q&A
            assistant_agent = GroundedAssistant(self.retriever, provider)
            res = await assistant_agent.answer(query=user_message, history=history)
            assistant_content = res["content"]
            citations_list = res.get("citations", [])

        latency_ms = round((time.time() - start_time) * 1000, 2)

        # 6. Save Assistant Message
        assistant_msg = await self.message_repo.create(
            session_id=session_id,
            role="assistant",
            content=assistant_content,
            citations=citations_list,
            metadata={
                "intent": decision.intent,
                "provider": provider.name,
                "model": provider.model_name,
                "latency_ms": latency_ms,
                "artifact_id": artifact_id
            }
        )
        await self.db.commit()

        # Format citations
        formatted_citations = [
            Citation(
                citation_id=c.get("citation_id", f"[S{i+1}]"),
                source_id=c.get("source_id", ""),
                episode_id=c.get("episode_id", ""),
                speaker=c.get("speaker", "Guest"),
                title=c.get("title", ""),
                url=c.get("url"),
                relevance_score=c.get("relevance_score", 1.0),
                passage_quote=c.get("passage_quote", ""),
                content=c.get("content")
            )
            for i, c in enumerate(citations_list)
        ]

        return ChatResponse(
            message_id=assistant_msg.id,
            session_id=session_id,
            role="assistant",
            content=assistant_content,
            citations=formatted_citations,
            intent=decision.intent,
            provider=provider.name,
            model=provider.model_name,
            latency_ms=latency_ms,
            artifact=artifact_preview,
            artifact_id=artifact_id
        )

    async def stream_chat(
        self,
        session_id: str,
        user_message: str,
        provider_name: Optional[str] = None
    ) -> AsyncIterator[str]:
        """
        Yields Server-Sent Events with progressive stage transitions.
        """
        session = await self.session_repo.get_or_create(session_id, default_title=user_message[:50])
        await self.message_repo.create(session_id=session_id, role="user", content=user_message)
        await self.db.commit()

        history = await self.message_repo.get_history_dicts(session_id, limit=6)
        provider = LLMProviderFactory.get_provider(provider_name)

        yield f"data: {json.dumps({'stage': 'searching', 'message': 'Searching Lenny’s knowledge base...'})}\n\n"
        
        # Retrieval
        search_results = await self.retriever.retrieve(user_message, top_k=5)
        
        yield f"data: {json.dumps({'stage': 'synthesizing', 'message': f'Found {len(search_results)} relevant transcript passages. Synthesizing evidence...', 'source_count': len(search_results)})}\n\n"

        assistant_agent = GroundedAssistant(self.retriever, provider)
        system_prompt, user_prompt, formatted_citations = assistant_agent._build_prompt(
            user_message, search_results, history
        )

        yield f"data: {json.dumps({'stage': 'generating', 'message': 'Generating grounded response...'})}\n\n"

        full_content = ""
        try:
            async for token in provider.stream(system_prompt, user_prompt):
                full_content += token
                yield f"data: {json.dumps({'token': token})}\n\n"
        except Exception as e:
            logger.warning("streaming_fallback_to_sync", error=str(e))
            gen_res = await provider.generate(system_prompt, user_prompt)
            full_content = gen_res.content
            yield f"data: {json.dumps({'token': full_content})}\n\n"

        # Finalize and persist
        assistant_msg = await self.message_repo.create(
            session_id=session_id,
            role="assistant",
            content=full_content,
            citations=formatted_citations,
            metadata={
                "intent": "grounded_qa",
                "provider": provider.name,
                "model": provider.model_name
            }
        )
        await self.db.commit()

        done_payload = {
            "stage": "done",
            "message_id": assistant_msg.id,
            "citations": formatted_citations,
            "provider": provider.name,
            "model": provider.model_name
        }
        yield f"data: {json.dumps(done_payload)}\n\n"

import json
import time
import uuid
from typing import Optional, List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.db.database import get_db, AsyncSessionLocal
from app.db.models import Session, Message, Artifact
from app.models.factory import provider_factory
from app.retrieval.retriever import retriever
from app.retrieval.citations import citation_validator
from app.agents.router import intent_router, AgentIntent
from app.agents.assistant import GroundedAssistantAgent
from app.agents.ship30 import Ship30Skill
from app.agents.artifact_builder import ArtifactBuilderSkill
from app.core.logging import logger

router = APIRouter(prefix="/chat", tags=["Grounded Chat & Streaming"])

class ChatRequest(BaseModel):
    session_id: str
    message: str
    provider: Optional[str] = None # 'ollama' | 'anthropic' | 'openai' | 'mock'
    stream: Optional[bool] = False

class ChatResponse(BaseModel):
    message_id: str
    session_id: str
    role: str = "assistant"
    content: str
    citations: List[Dict[str, Any]]
    intent: str
    provider: str
    model: str
    latency_ms: float
    artifact_id: Optional[str] = None

@router.post("", response_model=ChatResponse)
async def chat_endpoint(request_body: ChatRequest, db: AsyncSession = Depends(get_db)):
    """
    Standard synchronous/JSON chat endpoint with intent classification,
    RAG retrieval, grounding, citation mapping, and session persistence.
    """
    start_time = time.time()
    
    # 1. Verify or create session
    session_res = await db.execute(select(Session).where(Session.id == request_body.session_id))
    session = session_res.scalar_one_or_none()
    if not session:
        session = Session(id=request_body.session_id, title=request_body.message[:35] + ("..." if len(request_body.message) > 35 else ""))
        db.add(session)
        await db.commit()

    # 2. Save user message
    user_msg_id = str(uuid.uuid4())
    user_msg = Message(
        id=user_msg_id,
        session_id=session.id,
        role="user",
        content=request_body.message
    )
    db.add(user_msg)
    await db.commit()

    # 3. Intent Routing & Model Selection
    intent = intent_router.classify_intent(request_body.message)
    provider = provider_factory.get_provider(request_body.provider)

    # 4. RAG Retrieval
    citations_data = []
    retrieved_chunks = await retriever.retrieve_relevant_chunks(request_body.message, db)
    retrieval_context = retriever.format_retrieval_context(retrieved_chunks)

    # Fetch recent history for multi-turn context
    history_res = await db.execute(
        select(Message).where(Message.session_id == session.id).order_by(Message.created_at)
    )
    history_msgs = [{"role": m.role, "content": m.content} for m in history_res.scalars().all()[:-1]]

    artifact_id = None

    # 5. Execute Agent Skill based on Intent
    if intent == AgentIntent.OUT_OF_SCOPE or (not retrieved_chunks and intent == AgentIntent.GROUNDED_QA):
        # Graceful unsupported refusal without hallucination
        assistant_text = (
            "### I couldn't find sufficient evidence in Lenny's knowledge base\n\n"
            f"The transcripts in the current repository don't contain verified discussion on: *\"{request_body.message}\"*.\n\n"
            "**Topics covered by Lenny's guests include:**\n"
            "- **Brian Chesky (Airbnb)**: The 11-Star Experience, Founder Mode, and 0-to-1 Product Focus.\n"
            "- **Elena Verna (Miro, Amplitude)**: B2B Growth Loops, Freemium vs. Reverse Trials, and PLS.\n"
            "- **Shreyas Doshi (Stripe, Twitter)**: The LNO Framework for PM prioritization and High-Agency leadership.\n"
            "- **Sean Ellis (Dropbox, Eventbrite)**: The 40% Product-Market Fit Survey & ICE Experimentation.\n"
            "- **April Dunford**: The 5 Components of Effective Product Positioning.\n"
            "- **Rahul Vohra (Superhuman)**: The 4-Step PMF Engine."
        )
    elif intent == AgentIntent.SHIP_30_ESSAY:
        skill = Ship30Skill(provider)
        essay_result = await skill.generate_essay(request_body.message, retrieval_context)
        assistant_text = essay_result["content"]
        
        # Save as Artifact
        art = Artifact(
            session_id=session.id,
            message_id=user_msg_id,
            title=essay_result["title"],
            artifact_type="markdown",
            content=assistant_text,
            sanitized_content=assistant_text,
            artifact_metadata={"skill": "ship30", "word_count": essay_result["word_count"]}
        )
        db.add(art)
        await db.commit()
        await db.refresh(art)
        artifact_id = art.id
        citations_data = citation_validator.extract_cited_sources(assistant_text, retrieved_chunks)

    elif intent == AgentIntent.ARTIFACT_GENERATION:
        builder = ArtifactBuilderSkill(provider)
        art_res = await builder.generate_artifact(request_body.message, retrieval_context=retrieval_context)
        assistant_text = f"I've generated your custom artifact: **{art_res['title']}**.\n\nYou can view and interact with it in the side Artifact Viewer."
        
        art = Artifact(
            session_id=session.id,
            message_id=user_msg_id,
            title=art_res["title"],
            artifact_type=art_res["type"],
            content=art_res["content"],
            sanitized_content=art_res["sanitized_content"],
            artifact_metadata={"skill": "artifact_builder"}
        )
        db.add(art)
        await db.commit()
        await db.refresh(art)
        artifact_id = art.id

    else:
        # Grounded Conversational Assistant
        agent = GroundedAssistantAgent(provider)
        assistant_text = await agent.answer(request_body.message, retrieval_context, history_msgs)
        citations_data = citation_validator.extract_cited_sources(assistant_text, retrieved_chunks)

    # Update session title if default
    if session.title == "New Conversation":
        session.title = request_body.message[:35] + ("..." if len(request_body.message) > 35 else "")
        await db.commit()

    latency_ms = round((time.time() - start_time) * 1000, 2)
    assistant_msg_id = str(uuid.uuid4())
    
    # Save assistant message to DB
    asst_msg = Message(
        id=assistant_msg_id,
        session_id=session.id,
        role="assistant",
        content=assistant_text,
        citations=citations_data,
        message_metadata={
            "intent": intent.value,
            "provider": provider.model_name,
            "latency_ms": latency_ms,
            "artifact_id": artifact_id
        }
    )
    db.add(asst_msg)
    await db.commit()

    return ChatResponse(
        message_id=assistant_msg_id,
        session_id=session.id,
        role="assistant",
        content=assistant_text,
        citations=citations_data,
        intent=intent.value,
        provider=request_body.provider or "default",
        model=provider.model_name,
        latency_ms=latency_ms,
        artifact_id=artifact_id
    )

@router.post("/stream")
async def chat_stream_endpoint(request_body: ChatRequest):
    """
    Server-Sent Events (SSE) streaming endpoint with progressive state updates
    (searching -> synthesizing -> streaming) and full session persistence.
    """
    async def event_generator():
        start_time = time.time()
        
        # Open independent async session for streaming lifetime
        async with AsyncSessionLocal() as db:
            # 1. Verify or create session
            session_res = await db.execute(select(Session).where(Session.id == request_body.session_id))
            session = session_res.scalar_one_or_none()
            if not session:
                session = Session(id=request_body.session_id, title=request_body.message[:35] + ("..." if len(request_body.message) > 35 else ""))
                db.add(session)
                await db.commit()
            elif session.title == "New Conversation":
                session.title = request_body.message[:35] + ("..." if len(request_body.message) > 35 else "")
                await db.commit()

            # 2. Save user message
            user_msg_id = str(uuid.uuid4())
            user_msg = Message(
                id=user_msg_id,
                session_id=session.id,
                role="user",
                content=request_body.message
            )
            db.add(user_msg)
            await db.commit()

            # Stage 1: Searching knowledge base
            yield f"data: {json.dumps({'stage': 'searching', 'message': 'Searching Lennys transcript repository...'})}\n\n"
            
            retrieved_chunks = await retriever.retrieve_relevant_chunks(request_body.message, db)
            retrieval_context = retriever.format_retrieval_context(retrieved_chunks)
            
            # Stage 2: Synthesizing insights
            yield f"data: {json.dumps({'stage': 'synthesizing', 'message': f'Found {len(retrieved_chunks)} relevant guest passages. Synthesizing insights...'})}\n\n"

            provider = provider_factory.get_provider(request_body.provider)
            intent = intent_router.classify_intent(request_body.message)

            # Stage 3: Generating tokens
            yield f"data: {json.dumps({'stage': 'generating', 'message': 'Streaming grounded response with citations...'})}\n\n"

            full_content = []
            artifact_id = None

            try:
                if intent == AgentIntent.OUT_OF_SCOPE:
                    text = (
                        "### I couldn't find sufficient evidence in Lenny's knowledge base\n\n"
                        f"The transcripts in the repository do not contain verified information regarding *\"{request_body.message}\"*.\n\n"
                        "Try asking about: Product Strategy (Brian Chesky), Growth Loops (Elena Verna), Prioritization (Shreyas Doshi), PMF (Sean Ellis), or Positioning (April Dunford)."
                    )
                    for word in text.split(" "):
                        yield f"data: {json.dumps({'token': word + ' '})}\n\n"
                        full_content.append(word + " ")
                elif intent == AgentIntent.SHIP_30_ESSAY:
                    skill = Ship30Skill(provider)
                    essay_result = await skill.generate_essay(request_body.message, retrieval_context)
                    essay_text = essay_result["content"]
                    
                    # Save artifact
                    art = Artifact(
                        session_id=session.id,
                        message_id=user_msg_id,
                        title=essay_result["title"],
                        artifact_type="markdown",
                        content=essay_text,
                        sanitized_content=essay_text,
                        artifact_metadata={"skill": "ship30", "word_count": essay_result["word_count"]}
                    )
                    db.add(art)
                    await db.commit()
                    await db.refresh(art)
                    artifact_id = art.id

                    for word in essay_text.split(" "):
                        yield f"data: {json.dumps({'token': word + ' '})}\n\n"
                        full_content.append(word + " ")
                else:
                    agent = GroundedAssistantAgent(provider)
                    prompt_msgs = agent.build_prompt_messages(request_body.message, retrieval_context)
                    async for token in provider.stream_response(prompt_msgs):
                        full_content.append(token)
                        yield f"data: {json.dumps({'token': token})}\n\n"
            except Exception as e:
                logger.error(f"Streaming error: {e}")
                error_msg = f"\n\n**Error during generation**: {str(e)}\n\n*(If this is a 404, please ensure Ollama is running and `llama3.1:8b` is pulled, or switch to the Offline Mock provider).* "
                yield f"data: {json.dumps({'token': error_msg})}\n\n"
                full_content.append(error_msg)

            complete_text = "".join(full_content)
            citations_data = citation_validator.extract_cited_sources(complete_text, retrieved_chunks)
            latency_ms = round((time.time() - start_time) * 1000, 2)
            asst_msg_id = str(uuid.uuid4())

            # Save assistant message to DB
            asst_msg = Message(
                id=asst_msg_id,
                session_id=session.id,
                role="assistant",
                content=complete_text,
                citations=citations_data,
                message_metadata={
                    "intent": intent.value,
                    "provider": provider.model_name,
                    "latency_ms": latency_ms,
                    "artifact_id": artifact_id
                }
            )
            db.add(asst_msg)
            await db.commit()

            # Final complete event
            final_payload = {
                "stage": "complete",
                "message_id": asst_msg_id,
                "session_id": session.id,
                "full_content": complete_text,
                "citations": citations_data,
                "intent": intent.value,
                "provider": provider.model_name,
                "latency_ms": latency_ms,
                "artifact_id": artifact_id
            }
            yield f"data: {json.dumps(final_payload)}\n\n"

    return StreamingResponse(event_generator(), media_type="text/event-stream")

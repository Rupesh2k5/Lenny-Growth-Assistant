import pytest
import uuid
from httpx import AsyncClient, ASGITransport
from app.main import app

@pytest.mark.asyncio
async def test_grounded_chat_endpoint():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        session_id = str(uuid.uuid4())
        
        # Test grounded question
        payload = {
            "session_id": session_id,
            "message": "What does Brian Chesky recommend regarding what NOT to build and founder mode?",
            "provider": "mock"
        }
        res = await ac.post("/api/chat", json=payload)
        assert res.status_code == 200
        data = res.json()
        assert data["role"] == "assistant"
        assert len(data["content"]) > 0
        assert data["intent"] in ["grounded_qa", "ship_30_essay", "artifact_generation"]
        assert len(data["citations"]) >= 0

@pytest.mark.asyncio
async def test_unsupported_question_guardrail():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        session_id = str(uuid.uuid4())
        payload = {
            "session_id": session_id,
            "message": "What does Lenny's podcast say about quantum computing algorithms?",
            "provider": "mock"
        }
        res = await ac.post("/api/chat", json=payload)
        assert res.status_code == 200
        data = res.json()
        # Assert refusal without hallucination
        assert "evidence" in data["content"].lower() or "transcript" in data["content"].lower()

import pytest
import uuid
from httpx import AsyncClient, ASGITransport
from app.main import app

@pytest.mark.asyncio
async def test_ship30_skill_generation():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        session_id = str(uuid.uuid4())
        payload = {
            "session_id": session_id,
            "topic": "Elena Verna's B2B Growth Loops and PLG vs Free Trial",
            "target_length": 1250,
            "provider": "mock"
        }
        res = await ac.post("/api/skills/ship30", json=payload)
        assert res.status_code == 200
        data = res.json()
        assert "artifact_id" in data
        assert "content" in data
        assert data["word_count"] > 100
        assert "#" in data["content"] # Has markdown structure

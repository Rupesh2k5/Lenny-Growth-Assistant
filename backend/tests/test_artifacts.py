import pytest
import uuid
from httpx import AsyncClient, ASGITransport
from app.main import app

@pytest.mark.asyncio
async def test_artifact_generation_and_sanitization():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        session_id = str(uuid.uuid4())
        payload = {
            "session_id": session_id,
            "prompt": "Create an interactive Growth Loop Simulator HTML widget",
            "artifact_type": "html",
            "provider": "mock"
        }
        res = await ac.post("/api/skills/artifact", json=payload)
        assert res.status_code == 200
        data = res.json()
        artifact_id = data["artifact_id"]
        assert "sanitized_content" in data

        # Fetch artifact details
        get_res = await ac.get(f"/api/artifacts/{artifact_id}")
        assert get_res.status_code == 200
        art_detail = get_res.json()
        assert art_detail["id"] == artifact_id
        assert art_detail["type"] in ["html", "markdown"]

        # Fetch raw view
        raw_res = await ac.get(f"/api/artifacts/{artifact_id}/raw")
        assert raw_res.status_code == 200

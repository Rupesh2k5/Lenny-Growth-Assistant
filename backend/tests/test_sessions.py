import pytest
import uuid
from httpx import AsyncClient, ASGITransport
from app.main import app

@pytest.mark.asyncio
async def test_session_lifecycle():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        # 1. Create session
        create_res = await ac.post("/api/sessions", json={"title": "Test PM Session"})
        assert create_res.status_code == 201
        session_data = create_res.json()
        session_id = session_data["id"]
        assert session_data["title"] == "Test PM Session"

        # 2. List sessions
        list_res = await ac.get("/api/sessions")
        assert list_res.status_code == 200
        sessions = list_res.json()
        assert any(s["id"] == session_id for s in sessions)

        # 3. Update session title
        patch_res = await ac.patch(f"/api/sessions/{session_id}", json={"title": "Updated PM Session"})
        assert patch_res.status_code == 200
        assert patch_res.json()["title"] == "Updated PM Session"

        # 4. Get messages
        msg_res = await ac.get(f"/api/sessions/{session_id}/messages")
        assert msg_res.status_code == 200
        assert isinstance(msg_res.json(), list)

        # 5. Delete session
        del_res = await ac.delete(f"/api/sessions/{session_id}")
        assert del_res.status_code == 204

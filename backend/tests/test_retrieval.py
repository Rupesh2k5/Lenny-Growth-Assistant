import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app

@pytest.mark.asyncio
async def test_sources_and_retrieval():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        # Check indexed sources
        sources_res = await ac.get("/api/sources")
        assert sources_res.status_code == 200
        sources = sources_res.json()
        assert len(sources) > 0
        
        # Verify specific source exists
        source_id = sources[0]["id"]
        detail_res = await ac.get(f"/api/sources/{source_id}")
        assert detail_res.status_code == 200
        detail = detail_res.json()
        assert "speaker" in detail
        assert "full_text" in detail
        assert "chunks" in detail

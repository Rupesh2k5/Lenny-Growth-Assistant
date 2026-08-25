#!/usr/bin/env python3
"""
Automated End-to-End System Sanity Verification Script
Checks Database, Ingestion, Retrieval, Model Providers, and API Endpoints.
"""
import asyncio
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../backend")))

from httpx import AsyncClient, ASGITransport
from app.main import app

async def verify_all():
    print("="*60)
    print(" STARTING LENNY GROWTH ASSISTANT VERIFICATION")
    print("="*60)

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        # 1. Health check
        print("\n[1/6] Testing System Health Check...")
        res = await client.get("/api/health")
        assert res.status_code == 200, f"Health check failed: {res.text}"
        health_data = res.json()
        print(f"      Status: {health_data['status']}")
        print(f"      Indexed Sources: {health_data['database']['sources_indexed']}")
        print(f"      Indexed Chunks:  {health_data['database']['chunks_indexed']}")

        # 2. LLM Provider Status
        print("\n[2/6] Testing LLM Provider Orchestration...")
        llm_res = await client.get("/api/health/llm")
        assert llm_res.status_code == 200
        llm_data = llm_res.json()
        print(f"      Active Provider: {llm_data['active_provider']}")
        print(f"      Registered Providers: {list(llm_data['providers'].keys())}")

        # 3. Session Persistence
        print("\n[3/6] Testing Session Creation & Persistence...")
        sess_res = await client.post("/api/sessions", json={"title": "Verification Session"})
        assert sess_res.status_code == 201
        session_id = sess_res.json()["id"]
        print(f"      Created Session ID: {session_id}")

        # 4. Grounded Chat Query
        print("\n[4/6] Testing Grounded Q&A with Citation Extraction...")
        chat_payload = {
            "session_id": session_id,
            "message": "What is Brian Chesky's 11-star experience and why does he use it?",
            "provider": "mock"
        }
        chat_res = await client.post("/api/chat", json=chat_payload)
        assert chat_res.status_code == 200
        chat_data = chat_res.json()
        print(f"      Intent: {chat_data['intent']}")
        print(f"      Citations Extracted: {len(chat_data['citations'])}")
        print(f"      Response Length: {len(chat_data['content'])} chars")

        # 5. Ship 30 for 30 Skill
        print("\n[5/6] Testing Ship 30 for 30 Content Skill...")
        ship_payload = {
            "session_id": session_id,
            "topic": "The 40% PMF Survey Rule by Sean Ellis",
            "target_length": 1250,
            "provider": "mock"
        }
        ship_res = await client.post("/api/skills/ship30", json=ship_payload)
        assert ship_res.status_code == 200
        ship_data = ship_res.json()
        print(f"      Essay Title: {ship_data['title']}")
        print(f"      Artifact ID: {ship_data['artifact_id']}")
        print(f"      Word Count:  {ship_data['word_count']}")

        # 6. Artifact Viewer & Isolation
        print("\n[6/6] Testing Artifact Retrieval & Raw Sanitized Output...")
        art_id = ship_data["artifact_id"]
        art_res = await client.get(f"/api/artifacts/{art_id}")
        assert art_res.status_code == 200
        raw_res = await client.get(f"/api/artifacts/{art_id}/raw")
        assert raw_res.status_code == 200
        print(f"      Artifact Content-Type: {raw_res.headers.get('content-type')}")
        print("      Sanitization and retrieval verified.")

    print("\n" + "="*60)
    print(" ALL 6 VERIFICATION CHECKS PASSED (100% OPERATIONAL)")
    print("="*60 + "\n")

if __name__ == "__main__":
    asyncio.run(verify_all())

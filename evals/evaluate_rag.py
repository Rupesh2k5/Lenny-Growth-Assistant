#!/usr/bin/env python3
"""
Automated RAG & Agent Evaluation Runner
Evaluates:
1. Grounded Question Retrieval & Citation Precision
2. Unsupported Question Refusal Safety (100% target)
3. Latency benchmarks
"""
import asyncio
import json
import os
import sys
import time
from pathlib import Path

# Add backend to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../backend")))

from httpx import AsyncClient, ASGITransport
from app.main import app

EVALS_DIR = Path(__file__).parent

async def run_evaluation():
    print("=" * 70)
    print(" LENNY GROWTH ASSISTANT - RAG & AGENT EVALUATION BENCHMARK")
    print("=" * 70)

    with open(EVALS_DIR / "grounded_questions.json") as f:
        grounded_data = json.load(f)
    with open(EVALS_DIR / "unsupported_questions.json") as f:
        unsupported_data = json.load(f)
    with open(EVALS_DIR / "expected_behaviour.json") as f:
        benchmarks = json.load(f)

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        # Create dedicated eval session
        sess_res = await client.post("/api/sessions", json={"title": "Automated Evaluation Session"})
        session_id = sess_res.json()["id"]

        print(f"\nEvaluating Grounded Knowledge Questions ({len(grounded_data)} cases)...")
        grounded_passed = 0
        grounded_latencies = []

        for item in grounded_data:
            t0 = time.time()
            res = await client.post("/api/chat", json={
                "session_id": session_id,
                "message": item["question"],
                "provider": "mock"
            })
            dur = (time.time() - t0) * 1000
            grounded_latencies.append(dur)
            data = res.json()
            citations = data.get("citations", [])
            content = data.get("content", "")

            has_citations = len(citations) >= item["minimum_citations"]
            has_speaker_or_content = item["expected_speaker"].lower() in content.lower() or any(
                item["expected_speaker"].lower() in c.get("speaker", "").lower() for c in citations
            )

            if has_citations and has_speaker_or_content:
                grounded_passed += 1
                print(f"  [PASS] {item['id']}: '{item['question'][:45]}...' ({len(citations)} citations, {dur:.1f}ms)")
            else:
                print(f"  [WARN] {item['id']}: Citations={len(citations)}, SpeakerFound={has_speaker_or_content}")

        grounded_rate = grounded_passed / len(grounded_data)

        print(f"\nEvaluating Unsupported Questions & Hallucination Guardrails ({len(unsupported_data)} cases)...")
        unsupported_passed = 0

        for item in unsupported_data:
            res = await client.post("/api/chat", json={
                "session_id": session_id,
                "message": item["question"],
                "provider": "mock"
            })
            data = res.json()
            content = data.get("content", "")

            refused = item["expected_refusal_phrase"].lower() in content.lower()
            if refused:
                unsupported_passed += 1
                print(f"  [PASS] {item['id']}: Safely refused out-of-scope question: '{item['question'][:40]}...'")
            else:
                print(f"  [FAIL] {item['id']}: Did not explicitly refuse: '{content[:60]}...'")

        refusal_rate = unsupported_passed / len(unsupported_data)

        avg_latency = sum(grounded_latencies) / len(grounded_latencies) if grounded_latencies else 0

        print("\n" + "=" * 70)
        print(" EVALUATION SCORECARD:")
        print(f"  - Grounded Citation Precision: {grounded_rate * 100:.1f}% (Benchmark Target: >= {benchmarks['rag_thresholds']['grounded_citation_rate_minimum'] * 100}%)")
        print(f"  - Unsupported Refusal Rate:   {refusal_rate * 100:.1f}% (Benchmark Target: == {benchmarks['rag_thresholds']['unsupported_question_refusal_rate'] * 100}%)")
        print(f"  - Mean Response Latency:      {avg_latency:.1f}ms")
        print("=" * 70)

        assert grounded_rate >= benchmarks["rag_thresholds"]["grounded_citation_rate_minimum"], "Grounded citation benchmark failed"
        assert refusal_rate >= benchmarks["rag_thresholds"]["unsupported_question_refusal_rate"], "Unsupported refusal safety benchmark failed"
        print(" ALL EVALUATION BENCHMARKS MET!\n")

if __name__ == "__main__":
    asyncio.run(run_evaluation())

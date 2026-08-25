#!/usr/bin/env python3
"""
Transcript Ingestion CLI Script
Ingests all markdown transcripts from data/transcripts/ into the local or Postgres vector database.
"""
import asyncio
import os
import sys

# Add backend directory to python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../backend")))

from app.db.database import init_db, AsyncSessionLocal
from app.retrieval.ingestion import ingestion_service
from app.core.logging import logger

async def main():
    logger.info("Initializing database...")
    await init_db()
    
    async with AsyncSessionLocal() as session:
        logger.info("Starting transcript ingestion from data/transcripts/...")
        result = await ingestion_service.ingest_all_transcripts(session)
        print("\n" + "="*50)
        print(" TRANSCRIPT INGESTION COMPLETE")
        print(f" Sources Indexed: {result['ingested_sources']}")
        print(f" Chunks Indexed:  {result['ingested_chunks']}")
        print("="*50 + "\n")

if __name__ == "__main__":
    asyncio.run(main())

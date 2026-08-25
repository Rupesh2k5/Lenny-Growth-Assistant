import os
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.core.config import settings
from app.core.logging import logger, RequestLoggingMiddleware
from app.core.errors import AppError
from app.db.database import init_db, AsyncSessionLocal
from app.retrieval.ingestion import ingestion_service

from app.api.health import router as health_router
from app.api.sessions import router as sessions_router
from app.api.chat import router as chat_router
from app.api.skills import router as skills_router
from app.api.artifacts import router as artifacts_router
from app.api.sources import router as sources_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Initialize Database & Ingest Transcripts if empty
    logger.info("Initializing database schema...")
    await init_db()
    
    async with AsyncSessionLocal() as session:
        try:
            logger.info("Checking and indexing transcript corpus...")
            res = await ingestion_service.ingest_all_transcripts(session)
            logger.info(f"Ingestion result: {res}")
        except Exception as e:
            logger.error(f"Transcript auto-ingestion error on startup: {e}")

    yield

    # Shutdown
    logger.info("Shutting down Lenny Growth Assistant API service...")

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="Production-grade AI Growth Assistant grounded in Lenny's Podcast and Newsletter knowledge base.",
    lifespan=lifespan
)

# Request-ID & Structured Logging Middleware
app.add_middleware(RequestLoggingMiddleware)

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Domain AppError Exception Handler
@app.exception_handler(AppError)
async def app_error_handler(request: Request, exc: AppError):
    req_id = getattr(request.state, "request_id", "unknown")
    logger.warning(
        f"Domain AppError on {request.url.path}: [{exc.code}] {exc.message}",
        extra={"request_id": req_id, "error_code": exc.code}
    )
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": {
                "code": exc.code,
                "message": exc.message,
                "request_id": req_id,
                "retryable": exc.retryable,
                "details": exc.details
            }
        }
    )

# Global Unhandled Exception Handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    req_id = getattr(request.state, "request_id", "unknown")
    logger.error(f"Unhandled Exception on {request.url.path}: {exc}", extra={"request_id": req_id})
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": {
                "code": "INTERNAL_SERVER_ERROR",
                "message": "An unexpected error occurred while processing your request.",
                "request_id": req_id,
                "retryable": True,
                "details": str(exc) if settings.DEBUG else None
            }
        }
    )

# Include API Routers
api_prefix = settings.API_PREFIX
app.include_router(health_router, prefix=api_prefix)
app.include_router(sessions_router, prefix=api_prefix)
app.include_router(chat_router, prefix=api_prefix)
app.include_router(skills_router, prefix=api_prefix)
app.include_router(artifacts_router, prefix=api_prefix)
app.include_router(sources_router, prefix=api_prefix)

@app.get("/")
async def root():
    return {
        "app": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "docs_url": "/docs",
        "health_check": f"{settings.API_PREFIX}/health"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)

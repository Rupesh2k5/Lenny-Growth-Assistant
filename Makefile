.PHONY: help install ingest seed run test docker-up docker-down

help:
	@echo "Lenny Growth Assistant - Available Commands:"
	@echo "  make install     Install backend and frontend dependencies"
	@echo "  make ingest      Ingest and chunk all podcast transcripts into vector store"
	@echo "  make seed        Seed sample demo conversations and artifacts"
	@echo "  make dev-backend Run FastAPI backend in development mode"
	@echo "  make dev-frontend Run Vite frontend in development mode"
	@echo "  make test        Run all automated backend unit & integration tests"
	@echo "  make verify      Run end-to-end system verification script"
	@echo "  make docker-up   Launch full stack with Docker Compose"
	@echo "  make docker-down Teardown Docker Compose services"

install:
	pip install -r backend/requirements.txt
	cd frontend && npm install

ingest:
	python scripts/ingest_transcripts.py

seed:
	python scripts/seed_database.py

verify:
	python scripts/verify_system.py

test:
	pytest backend/tests/ -v

dev-backend:
	cd backend && uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

dev-frontend:
	cd frontend && npm run dev

docker-up:
	docker compose up --build -d

docker-down:
	docker compose down -v

# Lenny Growth Assistant — FDE Handoff Manual

Welcome to the FDE Handoff Manual. This document provides everything you need to run, test, troubleshoot, and extend the Lenny Growth Assistant.

## 1. One-Command Startup

For a zero-configuration experience, use Docker Compose:

`ash
# 1. Copy the example environment variables
cp .env.example .env

# 2. Build and start the cluster
docker-compose up --build
`
*Note: Make sure Docker is running on your machine.*

This will start:
- Backend: http://localhost:8000
- Frontend: http://localhost:5173
- PostgreSQL Database

## 2. Configuration & Secrets

The configuration is managed via .env files. We never commit secrets. 
Please refer to .env.example for:
- Database connection strings
- Default LLM provider toggles
- API Keys for optional cloud models (OpenAI, Anthropic)
- Safe default Hyperparameters (CORS, RAG limits)

## 3. Observability (Logging)

The backend uses a structured JSON logger for deep observability.
- Look at docker-compose logs backend to diagnose issues.
- Logs include equest_id, HTTP status, and duration.
- Detailed logs cover model generations, RAG retrieval scores, and database errors.

## 4. Resilience Mechanics

The system handles common errors gracefully:
- **Missing API Keys:** If you switch to Anthropic without a key, the backend returns a clear error instead of crashing.
- **Unavailable Ollama:** A friendly fallback message prompts you to start your local Ollama daemon.
- **Model Timeouts:** LLM calls have built-in timeout logic and fallback mechanisms.
- **Empty Retrieval:** The Agent Intent Router detects out-of-scope queries and refuses to hallucinate.

## 5. Testing & Extending

- **Automated Tests:** Run pytest backend/tests to execute unit tests.
- **Manual FDE Scenarios:** See docs/manual-test-plan.md for specific test scenarios to validate FDE expectations.
- **Extending Skills:** Add a new skill (like Ship 30) in ackend/app/agents/. Define the prompt and metadata requirements.
- **Adding LLM Providers:** Implement BaseLLMProvider in ackend/app/models/ and register it in provider_factory.py.

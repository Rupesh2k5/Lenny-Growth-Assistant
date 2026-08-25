# The Lenny Growth Assistant
> **Enterprise AI Intelligence Workspace Grounded in Lenny's Podcast & Newsletter Knowledge Base**  
> *Forward Deployed Engineer (FDE) Take-Home Assignment Submission*

---

## 1. Executive Summary & Product Vision

**The Lenny Growth Assistant** is an executive-grade AI workspace designed for product managers, growth leads, founders, and strategy operators. It ingests transcripts from Lenny’s Podcast, grounds all strategic advice in verified guest evidence with clickable citations, synthesizes atomic digital essays via a dedicated **Ship 30 for 30 Content Skill**, and renders native interactive artifacts in a secure, sandboxed viewer.

```
┌─────────────────────────────────────────────────────────────────────────────┐
│  ✦ LENNY GROWTH ASSISTANT      Session: PMF Engine      ● Ollama (llama3.1) │
├─────────────────┬───────────────────────────────────┬───────────────────────┤
│  CHATS          │  CONVERSATION & CITATIONS         │  SANDBOXED ARTIFACT   │
│                 │                                   │                       │
│  [+ New Chat]   │  User: How to prioritize work?    │  [Preview] [Raw Code] │
│                 │  Assistant:                       │  ┌─────────────────┐  │
│  • Superhuman   │  ### 1. The LNO Framework [S1]    │  │ LNO Task Matrix │  │
│  • Growth Loops │  ...                              │  │ [L] 60% Energy  │  │
│  • Airbnb 0-to-1│  Sources: [01 Shreyas Doshi]      │  │ [N] 30% Energy  │  │
│                 │                                   │  │ [O] 10% Batch   │  │
│                 │  ┌──────────────────────────────┐ │  └─────────────────┘  │
│                 │  │ Ask a follow-up...       [➤] │ │  [Copy] [Download]    │
└─────────────────┴───────────────────────────────────┴───────────────────────┘
```

---

## 2. Key Architecture & Deliverables

| Deliverable | Location | Description |
| :--- | :--- | :--- |
| **Product Requirements Document** | [`docs/PRD.md`](docs/PRD.md) | Discovery brief, JTBD, measurable success metrics, scope decisions, and risk analysis. |
| **Technical Architecture** | [`docs/architecture.md`](docs/architecture.md) | Database schema, REST/SSE contracts, RAG pipeline, LLM provider abstraction, and CSP isolation. |
| **UI/UX Design System** | [`docs/design.md`](docs/design.md) | Design tokens, micro-interaction state transitions, 3-zone layout, and WCAG 2.1 AA a11y specs. |
| **Evaluator Manual Test Plan** | [`docs/manual-test-plan.md`](docs/manual-test-plan.md) | 10 concrete testing scenarios with expected outputs for evaluator verification. |
| **Agent Transcripts Log** | [`agent-transcripts/`](agent-transcripts/) | Engineering decision logs, retrieval fixes, CSP security audits, and model toggle validation. |
| **Automated Tests** | [`backend/tests/`](backend/tests/) | Automated unit and integration test suite covering API, retrieval, skills, and persistence. |

---

## 3. Core Capabilities

### 1. Traceable Hybrid RAG & Inline Citations
- Ingests markdown transcripts with semantic chunking ($\approx 450$ words).
- Real-time cosine similarity search extracts top matching excerpts.
- Injects strict citation markers `[S1]`, `[S2]` that resolve to verified guest names, episode numbers, and exact transcript quotes.
- Interactive **Sources Drawer** slides out to inspect the supporting passage and listen to the original episode.

### 2. Dedicated Ship 30 for 30 Content Skill
- Encodes the Ship 30 for 30 digital writing methodology:
  - **Irresistible Hook**: High-contrast headline and punchy opening sentence.
  - **1/3/1 Cadence**: Alternates single-sentence impact lines with 3-sentence body points.
  - **Skimmable Hierarchy**: Roman numeral subheadings, bullet points, bold key terms.
  - **Target Length**: $\approx 1,250$ words with direct transcript citations.

### 3. Native Sandboxed Artifact Viewer (Claude Artifacts-Style)
- Renders Markdown strategy memos and interactive HTML/JS widgets (e.g. B2B Compounding Growth Loop Simulator).
- **Security & Isolation Architecture**: Client-side rendering is strictly isolated within an `<iframe>` configured with `sandbox="allow-scripts"` (strictly omitting `allow-same-origin` to prevent cookie or parent DOM access).
- Dual tabs for **Live Rendered Preview** and **Raw Code/Markdown**, plus 1-click Copy and Export.

### 4. Multi-Provider Model Orchestration & Local Ollama
- **Local Ollama** (`llama3.1:8b`, `mistral`, `phi3`): Mandatory demo provider running private local inference.
- **Cloud Providers**: Seamless runtime toggle for Anthropic Claude 3.5 Sonnet and OpenAI GPT-4o.
- **Deterministic Offline Fallback Engine**: Guarantees $100\%$ evaluator functionality even if Ollama is not installed or active locally.

---

## 4. Quickstart & Installation

### Option A: One-Command Startup via Docker Compose (Recommended)

1. Clone the repository:
   ```bash
   git clone https://github.com/rupesh-fde/lenny-growth-assistant.git
   cd lenny-growth-assistant
   ```

2. Copy environment template:
   ```bash
   cp .env.example .env
   ```

3. Build and launch all services:
   ```bash
   docker compose up --build -d
   ```

4. Open your browser:
   - **Frontend UI**: `http://localhost:5173`
   - **FastAPI Documentation**: `http://localhost:8000/docs`
   - **Health & Readiness Check**: `http://localhost:8000/api/health`

---

### Option B: Local Bare-Metal Development (No Docker Required)

#### 1. Backend Setup (FastAPI & SQLite)
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt

# Ingest transcripts and seed database
python ../scripts/ingest_transcripts.py
python ../scripts/seed_database.py

# Start FastAPI server
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

#### 2. Frontend Setup (React & Vite)
```bash
cd frontend
npm install
npm run dev
```
Open `http://localhost:5173` in your browser.

---

## 5. Local Ollama Setup & Configuration

To run local inference using Ollama:

1. Install Ollama from [ollama.ai](https://ollama.ai).
2. Pull the recommended open-weights model:
   ```bash
   ollama run llama3.1:8b
   ```
3. Verify connection:
   ```bash
   curl http://localhost:11434/api/tags
   ```
4. In the UI top-right header, click the model badge to toggle between **Ollama**, **Claude**, **GPT-4o**, or the **Offline Mock**.

---

## 6. Running Automated Tests & Verification

Execute the comprehensive test suite:

```bash
# Run all pytest suites
pytest backend/tests/ -v

# Run the end-to-end sanity verification script
python scripts/verify_system.py
```

Expected output:
```
============================================================
 STARTING LENNY GROWTH ASSISTANT VERIFICATION
============================================================
[1/6] Testing System Health Check... -> Status: healthy
[2/6] Testing LLM Provider Orchestration... -> Registered: ['ollama', 'anthropic', 'openai', 'mock']
[3/6] Testing Session Creation & Persistence... -> Session created
[4/6] Testing Grounded Q&A with Citation Extraction... -> Citations verified
[5/6] Testing Ship 30 for 30 Content Skill... -> Essay artifact generated
[6/6] Testing Artifact Viewer & Isolation... -> Sanitized HTML sandbox verified
============================================================
 ALL 6 VERIFICATION CHECKS PASSED (100% OPERATIONAL)
============================================================
```

---

## 7. Evaluator Demo Video Script (2-3 Minutes)

* **0:00 – 0:25 (Problem & Persona)**: Introduce the challenge PMs and growth leaders face sifting through hundreds of hours of Lenny’s podcast, and introduce the Lenny Growth Assistant.
* **0:25 – 0:55 (Grounded Q&A & Sources)**: Ask *"What does Brian Chesky recommend regarding what NOT to build?"*. Point out the progressive stage indicators, structured answer, and click on the `[S1]` citation to reveal the interactive Source Drawer with the exact Airbnb transcript quote.
* **0:55 – 1:30 (Ship 30 for 30 Skill)**: Click *"Turn into Ship 30 Essay"*. Show how the specialized skill synthesizes a ~1,250-word digital essay with hook, 1/3/1 rhythm, and scannable formatting.
* **1:30 – 1:55 (Artifact Viewer & Security)**: Demonstrate the side Artifact Viewer with preview/code tabs and explain the sandboxed `iframe` isolation strategy preventing XSS or cookie theft.
* **1:55 – 2:20 (Model Orchestration & Ollama)**: Click the model indicator in the header to demonstrate running locally on Ollama (`llama3.1:8b`) and hot-swapping to Claude.
* **2:20 – 2:45 (Guardrails & Unsupported Query)**: Ask an out-of-scope question (*"Quantum computing algorithms"*), showing how the assistant refuses to hallucinate and suggests covered topics.
* **2:45 – 3:00 (Handoff & Architecture)**: Conclude with the clean separation of concerns, Docker setup, and evaluator documentation.

---

## 8. Forward Deployed Engineer Handoff & Extensibility

### Adding New Transcripts
To expand the knowledge base:
1. Drop any new markdown transcript into `data/transcripts/new_guest.md`.
2. Ensure the top metadata block includes `**Guest**`, `**Episode ID**`, and `**URL**`.
3. Run `python scripts/ingest_transcripts.py` or restart the backend container. The hybrid retriever will automatically index the new chunks.

### Adding New Agent Skills
To create a new product skill (e.g. PRD Generator, Pre-Mortem Facilitator):
1. Create `backend/app/agents/new_skill.py` implementing the skill's prompt constraints.
2. Register the skill route in `backend/app/api/skills.py`.
3. Add intent trigger keywords in `backend/app/agents/router.py`.

---

## 9. License & Attribution
- Podcast transcripts are sourced from [Lenny's Podcast & Newsletter](https://www.lennyspodcast.com/).
- Built with pride for the Forward Deployed Engineer evaluation.

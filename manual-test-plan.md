# Evaluator Manual Test Plan & Verification Protocol
## The Lenny Growth Assistant

---

## 1. Purpose & Overview
This document provides evaluators with a 10-step, end-to-end verification checklist to test all core capabilities of **The Lenny Growth Assistant**: Grounded QA, Source Citation, Ship 30 for 30 Content Skill, Sandboxed Artifact Viewer, Model Switching, Unsupported Query Handling, and Persistence.

---

## 2. Test Scenarios

### Scenario 1: Initial Workspace State & Prompts
* **Action**: Open `http://localhost:5173`.
* **Expected Result**:
  - Application displays 3-zone layout with header, sidebar, chat area, and suggested prompt chips.
  - Active model indicator in the top right shows active provider (e.g. `Ollama (llama3.1:8b)` or configured cloud model).
  - No broken images, console errors, or unrendered layout blocks.

### Scenario 2: Grounded Product Question with Citations
* **Action**: Click the prompt chip *"How should a startup decide what NOT to build?"* or submit:
  `"What does Brian Chesky recommend regarding what NOT to build and founder mode?"`
* **Expected Result**:
  - Backend shows live progressive stages (*Searching* $\to$ *Synthesizing* $\to$ *Generating*).
  - Assistant returns a structured response citing `[S1] Brian Chesky (Airbnb)` and explains avoiding "indigestion over starvation" and the 6-month seasonal release reviews.
  - Expandable **Sources (1)** card appears below the message.

### Scenario 3: Source Inspection Drawer
* **Action**: Click on the `[S1]` inline badge or the `Brian Chesky — Leading Airbnb` source card.
* **Expected Result**:
  - Sources Drawer opens on the right side.
  - Displays Guest Name (`Brian Chesky`), Episode ID (`EP-101`), Relevance Score ($\approx 90-95\%$), and the exact quote from the transcript.

### Scenario 4: Ship 30 for 30 Content Skill
* **Action**: Click the *"Turn into Ship 30 Essay"* button on the message or submit:
  `"Write a Ship 30 for 30 essay on Elena Verna's B2B growth loops and freemium vs free trial."`
* **Expected Result**:
  - Intent router classifies query to `Ship30Skill`.
  - Generates a full $\sim 1,250$-word essay with a compelling hook, 1/3/1 formatting, bold takeaways, and transcript grounding.
  - The **Artifact Viewer** panel automatically opens on the right displaying the styled essay.

### Scenario 5: Interactive HTML/CSS Artifact Generation
* **Action**: Submit:
  `"Generate an interactive HTML/JS growth loop simulator based on Elena Verna's framework."`
* **Expected Result**:
  - The Artifact Viewer displays an interactive HTML component with range sliders and calculated compounding outputs.
  - Toggling between **Preview** and **Raw Code** displays clean syntax-highlighted code.
  - Sandboxed isolation prevents any popup or external script injection.

### Scenario 6: Unsupported Query & Hallucination Guardrail
* **Action**: Submit:
  `"What does Lenny's podcast say about quantum computing algorithms and dark matter?"`
* **Expected Result**:
  - Assistant responds with polite transparency: *"I could not find sufficient evidence about quantum computing algorithms in Lenny's transcript knowledge base."*
  - Provides a list of topics covered in the transcripts (Product Strategy, Growth Loops, PMF, Pricing).
  - Does NOT fabricate any fake guest quotes.

### Scenario 7: Multi-Provider Model Toggle
* **Action**: Click the **Model Selector** in the header (`Ollama ●`).
* **Expected Result**:
  - Modal/Dropdown shows available providers (Ollama, Anthropic Claude, OpenAI).
  - Switching provider updates the active badge immediately without requiring an application restart.
  - If Ollama is offline, the UI indicates fallback status clearly.

### Scenario 8: Session Persistence & Multi-Chat
* **Action**: Click `+ New Chat` in the sidebar. Start a conversation about `Sean Ellis PMF Survey 40% rule`.
* **Expected Result**:
  - New session is created with its own isolated message history.
  - Previous sessions remain visible and switchable in the sidebar.
  - Reloading the browser page preserves all sessions and conversation messages.

### Scenario 9: Artifact Export (Copy & Download)
* **Action**: In the Artifact Viewer, click `Copy` and `Download`.
* **Expected Result**:
  - Copy copies full Markdown/HTML to system clipboard with a visual checkmark toast.
  - Download saves `.md` or `.html` file locally with a descriptive filename.

### Scenario 10: API Health & Observability Endpoints
* **Action**: Run `curl http://localhost:8000/api/health` and `curl http://localhost:8000/api/health/llm`.
* **Expected Result**:
  - Returns `status: "healthy"`, database status, active LLM provider, and total ingested transcript chunk count.

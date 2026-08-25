# UI/UX Design System & Experience Specifications
## The Lenny Growth Assistant

---

## 1. Design Principles

1. **Executive Clarity & Restraint**: Avoid loud gimmicks. Treat the interface as a mission-critical intelligence tool for founders, VPs, and product leads.
2. **Immediate Cognitive Affordance**: Never present an intimidating empty text box. Guide the user with clear intent entry points (Ask Lenny, Write with Lenny, Interactive Artifacts).
3. **Traceability as a First-Class Citizen**: Every piece of AI knowledge must wear its source openly. Citations are not hidden footnotes; they are interactive, scannable bridges to real human conversations.
4. **Side-by-Side Artifact Flow**: Artifacts shouldn't be dumped inside a narrow chat bubble. They render in a dedicated, resizable workspace beside the chat.

---

## 2. Layout & Spatial Hierarchy

The application employs a 3-Zone Workspace layout:

```
┌─────────────────────────────────────────────────────────────────────────────┐
│ ✦ LENNY GROWTH ASSISTANT       [Session Title]       ● Ollama (llama3.1) [⚙]│
├─────────────────┬───────────────────────────────────┬───────────────────────┤
│                 │                                   │                       │
│  SESSIONS       │           CHAT TIMELINE           │    ARTIFACT VIEWER    │
│                 │                                   │                       │
│  [+ New Chat]   │  User: How to prioritize PM tasks?│  [Preview] [Raw Code] │
│                 │                                   │  ┌─────────────────┐  │
│  • PMF Engine   │  Assistant:                       │  │ LNO Task Matrix │  │
│  • Growth Loops │  ### 1. The LNO Framework [S1]    │  │                 │  │
│  • Airbnb 0-to-1│  ...                              │  │ [L] 60% Energy  │  │
│  • Pricing & PLG│                                   │  │ [N] 30% Energy  │  │
│                 │  Sources [2 Sources]              │  │ [O] 10% Batch   │  │
│                 │  ┌──────────────────────────────┐ │  └─────────────────┘  │
│                 │  │ 01 Shreyas Doshi • EP-103    │ │                       │
│                 │  └──────────────────────────────┘ │  [Copy] [Download]    │
│                 │                                   │                       │
│                 │  ┌──────────────────────────────┐ │                       │
│                 │  │ Ask a follow-up...       [➤] │ │                       │
│                 │  └──────────────────────────────┘ │                       │
└─────────────────┴───────────────────────────────────┴───────────────────────┘
```

---

## 3. Color Tokens & Visual System

* **Background (Canvas)**: `#0F1117` (Deep Dark Obsidian) / `#F9FAFB` (Clean Light)
* **Surface Panels**: `#161922` / `#FFFFFF`
* **Card Borders**: `#262B3B` / `#E5E7EB`
* **Primary Text**: `#F3F4F6` / `#111827`
* **Secondary Text**: `#9CA3AF` / `#4B5563`
* **Brand Accent (Lenny Warm Gold)**: `#F59E0B` (Amber 500) & `#D97706` (Amber 600)
* **Citation Tag**: `#3B82F6` (Blue 500)
* **Status Badge (Online)**: `#10B981` (Emerald 500)

---

## 4. Micro-Interactions & State Progression

### 4.1 Message Submission States
Instead of an opaque generic loader, the chat displays progressive backend phases:
1. `Searching Lenny's knowledge base...` (Vector similarity search)
2. `Synthesizing insights from guests...` (Prompt formatting & context injection)
3. `Streaming response with citations...` (Token delivery)

### 4.2 Citation Interaction
* **Hover**: Tooltip with guest name, episode title, and relevance %.
* **Click**: Slides open the **Sources Drawer** with the exact highlighted passage quote and a link to the full podcast episode.

### 4.3 Artifact Transition
* When an artifact skill runs or is requested, the right-hand **Artifact Viewer** panel automatically expands with a smooth slide-over transition, immediately streaming the rendered HTML/Markdown preview.

---

## 5. Accessibility (a11y) & WCAG 2.1 AA Compliance

* **Keyboard Navigation**: Full `Tab` / `Shift+Tab` focus trap inside modals; `Ctrl+Enter` to submit messages; `Escape` to close drawers.
* **Focus States**: High-contrast focus rings (`ring-2 ring-amber-500 ring-offset-2`).
* **ARIA Semantics**: `role="log"`, `aria-live="polite"` for streaming chat messages, `aria-expanded` on accordion source cards.
* **Contrast Ratios**: Exceeds $4.5:1$ contrast ratio for standard text and $3:1$ for large titles.

import re
from enum import Enum
from typing import Dict, Any

class AgentIntent(str, Enum):
    GROUNDED_QA = "grounded_qa"
    SHIP_30_ESSAY = "ship_30_essay"
    ARTIFACT_GENERATION = "artifact_generation"
    OUT_OF_SCOPE = "out_of_scope"

class IntentRouter:
    """
    Classifies user prompt intent to route execution to specialized agent skills.
    """
    SHIP30_KEYWORDS = [
        "ship 30", "ship30", "write an essay", "write a 1250", "atomic essay",
        "turn this into an essay", "write an article", "essay style", "newsletter post"
    ]
    
    ARTIFACT_KEYWORDS = [
        "create an artifact", "generate an html", "interactive calculator",
        "growth loop simulator", "pmf calculator", "task matrix", "canvas",
        "render an artifact", "visualize a loop", "html/css"
    ]

    OUT_OF_SCOPE_KEYWORDS = [
        "quantum computing", "astrophysics", "cryptocurrency mining",
        "plumbing tutorial", "recipe for pizza", "fix my car engine"
    ]

    def classify_intent(self, prompt: str) -> AgentIntent:
        p_lower = prompt.lower()

        # Check out-of-scope
        for kw in self.OUT_OF_SCOPE_KEYWORDS:
            if kw in p_lower:
                return AgentIntent.OUT_OF_SCOPE

        # Check Ship 30 for 30 essay
        for kw in self.SHIP30_KEYWORDS:
            if kw in p_lower:
                return AgentIntent.SHIP_30_ESSAY

        # Check Artifact creation
        for kw in self.ARTIFACT_KEYWORDS:
            if kw in p_lower:
                return AgentIntent.ARTIFACT_GENERATION

        # Default is grounded QA
        return AgentIntent.GROUNDED_QA

intent_router = IntentRouter()

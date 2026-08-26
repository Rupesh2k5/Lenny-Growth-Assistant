from typing import List, Dict, Any, Optional
from app.models.provider import BaseLLMProvider

SHIP30_SYSTEM_PROMPT = """You are an expert digital essayist trained in the Ship 30 for 30 writing methodology, specialized in translating deep product management and growth wisdom into viral, high-signal essays.

ESSAY SPECIFICATIONS:
1. Target Length: Approximately 250 words.
2. Structure:
   - **Headline**: Irresistible, high-contrast, specific (e.g. "The 4-Step PMF Engine: Why 80% of Startups Scale Too Early").
   - **The Hook (First 3 sentences)**: Disrupt conventional wisdom immediately. Use short, punchy cadence.
   - **The 1/3/1 Writing Rhythm**: Alternate between single-sentence impact lines, 3-sentence explanatory paragraphs, and single-sentence takeaways.
   - **Subsections (3-4 core sections)**: Clear Roman numeral or numeric headings (`## 1. The Core Trap`, `## 2. The Proven Framework`).
   - **Formatting**: Heavy use of bold key terms, scannable bullet points, and high-impact quotes from Lenny's podcast guests.
   - **Grounding**: Seamlessly integrate real transcript insights and citations ([S1], [S2]) into the narrative.
   - **The Ultimate Takeaway**: An unambiguous, immediate action the reader can take today.
"""

class Ship30Skill:
    def __init__(self, provider: BaseLLMProvider):
        self.provider = provider

    def build_prompt_messages(self, topic: str, retrieval_context: str, target_length: int = 1250) -> list:
        user_prompt = f"""RETRIEVED KNOWLEDGE BASE EXCERPTS:
{retrieval_context}

TOPIC TO WRITE ABOUT:
{topic}

INSTRUCTIONS:
Write a full ~{target_length} word Ship 30 for 30 style essay synthesizing the retrieved insights. Include inline citations [S1], [S2] to ground all guest quotes and frameworks. Ensure strong headline and hook.
"""
        return [{"role": "user", "content": user_prompt}]

    def extract_title(self, content: str, default_topic: str) -> str:
        title_line = content.split("\n")[0].replace("#", "").strip() if content.startswith("#") else f"Ship 30 Essay: {default_topic}"
        return title_line

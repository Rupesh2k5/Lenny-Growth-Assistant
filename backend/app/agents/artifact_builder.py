from typing import List, Dict, Any, Optional
from app.models.provider import BaseLLMProvider
from app.core.security import sanitize_html_content

ARTIFACT_SYSTEM_PROMPT = """You are a senior frontend developer and product strategist capable of generating standalone, fully interactive HTML/CSS/JS widgets or structured Markdown documents for product management and growth teams.

ARTIFACT RULES:
1. If the user asks for an interactive tool, simulator, or visual calculator, output complete, standalone, beautiful HTML with inline CSS and vanilla JavaScript.
2. If the user asks for a PRD, memo, or strategy canvas, output formatted GitHub-flavored Markdown.
3. Keep designs modern, clean, with dark/light responsive styling, rounded cards, and smooth micro-interactions.
4. Ensure interactive tools calculate real product metrics (e.g. compounding growth loops, PMF % very disappointed, LNO score).
"""

class ArtifactBuilderSkill:
    def __init__(self, provider: BaseLLMProvider):
        self.provider = provider

    async def generate_artifact(
        self,
        prompt: str,
        artifact_type: str = "html", # 'html' | 'markdown'
        retrieval_context: str = ""
    ) -> Dict[str, Any]:
        user_prompt = f"""KNOWLEDGE BASE CONTEXT:
{retrieval_context}

REQUESTED ARTIFACT:
{prompt}

ARTIFACT FORMAT: {artifact_type.upper()}
Please generate the complete, self-contained artifact.
"""
        messages = [{"role": "user", "content": user_prompt}]
        response = await self.provider.generate_response(
            messages=messages,
            system_prompt=ARTIFACT_SYSTEM_PROMPT,
            temperature=0.5
        )

        content = response.content
        title = "Growth Strategy Artifact"

        # Determine type & sanitize
        if "html" in artifact_type.lower() or "<html" in content or "<div" in content:
            art_type = "html"
            sanitized = sanitize_html_content(content)
            title = "Interactive Growth Artifact"
        else:
            art_type = "markdown"
            sanitized = content
            first_line = content.split("\n")[0].replace("#", "").strip() if content.startswith("#") else "Strategy Document"
            title = first_line or "Strategy Document"

        return {
            "title": title,
            "type": art_type,
            "content": content,
            "sanitized_content": sanitized,
            "model": response.model,
            "provider": response.provider
        }

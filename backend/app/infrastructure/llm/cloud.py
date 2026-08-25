import os
from typing import Optional

from app.models.provider import BaseLLMProvider, LLMResponse
from app.models.anthropic_provider import AnthropicProvider
from app.models.openai_provider import OpenAIProvider
from app.models.ollama_provider import OllamaProvider
from app.core.config import settings

class CloudLLMProvider(BaseLLMProvider):
    """A provider that delegates to Anthropic or OpenAI based on the ``LLM_PROVIDER``
    environment variable (or the ``settings.DEFAULT_PROVIDER`` configuration)."""

    def __init__(self):
        provider_name = os.getenv("LLM_PROVIDER", settings.DEFAULT_PROVIDER).lower()
        if provider_name == "anthropic":
            if not settings.ANTHROPIC_API_KEY:
                raise ValueError("Anthropic API key not configured")
            self.provider: BaseLLMProvider = AnthropicProvider(
                model_name=settings.ANTHROPIC_MODEL,
                api_key=settings.ANTHROPIC_API_KEY,
            )
        elif provider_name == "openai":
            if not settings.OPENAI_API_KEY:
                raise ValueError("OpenAI API key not configured")
            self.provider = OpenAIProvider(
                model_name=settings.OPENAI_MODEL,
                api_key=settings.OPENAI_API_KEY,
            )
        else:
            # Fallback to Ollama (local) for free‑of‑cost usage
            self.provider = OllamaProvider(
                model_name=settings.OLLAMA_MODEL,
                base_url=settings.OLLAMA_BASE_URL,
            )

    async def generate_response(
        self,
        messages: list[dict[str, str]],
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
    ) -> LLMResponse:
        return await self.provider.generate_response(
            messages=messages,
            system_prompt=system_prompt,
            temperature=temperature,
        )

    async def stream_response(
        self,
        messages: list[dict[str, str]],
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
    ):
        async for token in self.provider.stream_response(
            messages=messages,
            system_prompt=system_prompt,
            temperature=temperature,
        ):
            yield token

    async def check_health(self) -> dict:
        return await self.provider.check_health()

import time
import httpx
from typing import List, Dict, Any, AsyncGenerator, Optional
from app.models.provider import BaseLLMProvider, LLMResponse
from app.core.config import settings
from app.core.logging import logger

class AnthropicProvider(BaseLLMProvider):
    def __init__(self, model_name: Optional[str] = None, api_key: Optional[str] = None):
        super().__init__(model_name=model_name or settings.ANTHROPIC_MODEL)
        self.api_key = api_key or settings.ANTHROPIC_API_KEY
        self.base_url = "https://api.anthropic.com/v1/messages"

    async def generate_response(
        self,
        messages: List[Dict[str, str]],
        system_prompt: Optional[str] = None,
        temperature: float = 0.7
    ) -> LLMResponse:
        if not self.api_key:
            raise ValueError("ANTHROPIC_API_KEY is not configured.")

        start_time = time.time()
        headers = {
            "x-api-key": self.api_key,
            "anthropic-version": "2023-06-01",
            "content-type": "application/json"
        }

        payload = {
            "model": self.model_name,
            "messages": messages,
            "max_tokens": 4096,
            "temperature": temperature
        }
        if system_prompt:
            payload["system"] = system_prompt

        async with httpx.AsyncClient(timeout=120.0) as client:
            response = await client.post(self.base_url, headers=headers, json=payload)
            response.raise_for_status()
            data = response.json()

            content = "".join([block.get("text", "") for block in data.get("content", [])])
            latency_ms = round((time.time() - start_time) * 1000, 2)

            return LLMResponse(
                content=content,
                model=self.model_name,
                provider="anthropic",
                latency_ms=latency_ms,
                usage=data.get("usage")
            )

    async def stream_response(
        self,
        messages: List[Dict[str, str]],
        system_prompt: Optional[str] = None,
        temperature: float = 0.7
    ) -> AsyncGenerator[str, None]:
        # Simple non-blocking yield if streaming API is accessed
        resp = await self.generate_response(messages, system_prompt, temperature)
        yield resp.content

    async def check_health(self) -> Dict[str, Any]:
        if not self.api_key:
            return {
                "status": "unconfigured",
                "provider": "anthropic",
                "message": "ANTHROPIC_API_KEY is not set in environment."
            }
        return {
            "status": "ready",
            "provider": "anthropic",
            "model": self.model_name,
            "message": "Anthropic Claude API Key configured."
        }

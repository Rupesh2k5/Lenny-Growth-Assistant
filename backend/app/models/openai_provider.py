import time
import httpx
from typing import List, Dict, Any, AsyncGenerator, Optional
from app.models.provider import BaseLLMProvider, LLMResponse
from app.core.config import settings
from app.core.logging import logger

class OpenAIProvider(BaseLLMProvider):
    def __init__(self, model_name: Optional[str] = None, api_key: Optional[str] = None):
        super().__init__(model_name=model_name or settings.OPENAI_MODEL)
        self.api_key = api_key or settings.OPENAI_API_KEY
        self.base_url = "https://api.openai.com/v1/chat/completions"

    async def generate_response(
        self,
        messages: List[Dict[str, str]],
        system_prompt: Optional[str] = None,
        temperature: float = 0.7
    ) -> LLMResponse:
        if not self.api_key:
            raise ValueError("OPENAI_API_KEY is not configured.")

        start_time = time.time()
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        formatted_messages = []
        if system_prompt:
            formatted_messages.append({"role": "system", "content": system_prompt})
        formatted_messages.extend(messages)

        payload = {
            "model": self.model_name,
            "messages": formatted_messages,
            "temperature": temperature
        }

        async with httpx.AsyncClient(timeout=120.0) as client:
            response = await client.post(self.base_url, headers=headers, json=payload)
            response.raise_for_status()
            data = response.json()

            content = data["choices"][0]["message"]["content"]
            latency_ms = round((time.time() - start_time) * 1000, 2)

            return LLMResponse(
                content=content,
                model=self.model_name,
                provider="openai",
                latency_ms=latency_ms,
                usage=data.get("usage")
            )

    async def stream_response(
        self,
        messages: List[Dict[str, str]],
        system_prompt: Optional[str] = None,
        temperature: float = 0.7
    ) -> AsyncGenerator[str, None]:
        resp = await self.generate_response(messages, system_prompt, temperature)
        yield resp.content

    async def check_health(self) -> Dict[str, Any]:
        if not self.api_key:
            return {
                "status": "unconfigured",
                "provider": "openai",
                "message": "OPENAI_API_KEY is not set in environment."
            }
        return {
            "status": "ready",
            "provider": "openai",
            "model": self.model_name,
            "message": "OpenAI API Key configured."
        }

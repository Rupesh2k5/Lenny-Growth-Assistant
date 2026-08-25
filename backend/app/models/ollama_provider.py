import time
import json
import httpx
from typing import List, Dict, Any, AsyncGenerator, Optional
from app.models.provider import BaseLLMProvider, LLMResponse
from app.core.config import settings
from app.core.logging import logger

class OllamaProvider(BaseLLMProvider):
    def __init__(self, model_name: Optional[str] = None, base_url: Optional[str] = None):
        super().__init__(model_name=model_name or settings.OLLAMA_MODEL)
        self.base_url = (base_url or settings.OLLAMA_BASE_URL).rstrip("/")

    async def generate_response(
        self,
        messages: List[Dict[str, str]],
        system_prompt: Optional[str] = None,
        temperature: float = 0.7
    ) -> LLMResponse:
        start_time = time.time()
        
        # Prepare Ollama chat payload
        formatted_messages = []
        if system_prompt:
            formatted_messages.append({"role": "system", "content": system_prompt})
        formatted_messages.extend(messages)

        payload = {
            "model": self.model_name,
            "messages": formatted_messages,
            "stream": False,
            "options": {
                "temperature": temperature,
                "num_ctx": 2048
            }
        }

        try:
            async with httpx.AsyncClient(timeout=600.0) as client:
                response = await client.post(
                    f"{self.base_url}/api/chat",
                    json=payload
                )
                response.raise_for_status()
                data = response.json()
                
                # Ollama may return the generated text either nested under
                # "message": {"content": "..."} or directly as "content".
                # Accept both formats to avoid key errors and ensure we capture the answer.
                content = data.get("message", {}).get("content", "") or data.get("content", "")
                latency_ms = round((time.time() - start_time) * 1000, 2)
                
                return LLMResponse(
                    content=content,
                    model=self.model_name,
                    provider="ollama",
                    latency_ms=latency_ms,
                    usage={
                        "prompt_eval_count": data.get("prompt_eval_count", 0),
                        "eval_count": data.get("eval_count", 0)
                    }
                )
        except Exception as e:
            logger.error(f"Ollama generation failed: {e}")
            raise

    async def stream_response(
        self,
        messages: List[Dict[str, str]],
        system_prompt: Optional[str] = None,
        temperature: float = 0.7
    ) -> AsyncGenerator[str, None]:
        formatted_messages = []
        if system_prompt:
            formatted_messages.append({"role": "system", "content": system_prompt})
        formatted_messages.extend(messages)

        payload = {
            "model": self.model_name,
            "messages": formatted_messages,
            "stream": True,
            "options": {
                "temperature": temperature,
                "num_ctx": 2048
            }
        }

        async with httpx.AsyncClient(timeout=300.0) as client:
            async with client.stream(
                "POST",
                f"{self.base_url}/api/chat",
                json=payload
            ) as response:
                response.raise_for_status()
                async for line in response.aiter_lines():
                    if line:
                        try:
                            chunk_data = json.loads(line)
                            chunk_text = chunk_data.get("message", {}).get("content", "")
                            if chunk_text:
                                yield chunk_text
                        except json.JSONDecodeError:
                            continue

    async def check_health(self) -> Dict[str, Any]:
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.get(f"{self.base_url}/api/tags")
                if response.status_code == 200:
                    models = [m.get("name") for m in response.json().get("models", [])]
                    is_model_present = any(self.model_name in m for m in models)
                    return {
                        "status": "healthy" if is_model_present else "warning",
                        "provider": "ollama",
                        "base_url": self.base_url,
                        "model": self.model_name,
                        "available_models": models,
                        "is_model_loaded": is_model_present,
                        "message": "Connected to Ollama local daemon" if is_model_present else f"Model {self.model_name} not yet pulled"
                    }
                return {
                    "status": "unhealthy",
                    "provider": "ollama",
                    "message": f"Ollama returned status {response.status_code}"
                }
        except Exception as e:
            return {
                "status": "unavailable",
                "provider": "ollama",
                "message": f"Ollama daemon not reachable at {self.base_url}: {str(e)}"
            }

from abc import ABC, abstractmethod
from typing import List, Dict, Any, AsyncGenerator, Optional
from pydantic import BaseModel

class LLMResponse(BaseModel):
    content: str
    model: str
    provider: str
    latency_ms: float
    usage: Optional[Dict[str, int]] = None

class BaseLLMProvider(ABC):
    def __init__(self, model_name: str):
        self.model_name = model_name

    @abstractmethod
    async def generate_response(
        self,
        messages: List[Dict[str, str]],
        system_prompt: Optional[str] = None,
        temperature: float = 0.7
    ) -> LLMResponse:
        """Generate a complete non-streaming response."""
        pass

    @abstractmethod
    async def stream_response(
        self,
        messages: List[Dict[str, str]],
        system_prompt: Optional[str] = None,
        temperature: float = 0.7
    ) -> AsyncGenerator[str, None]:
        """Stream response tokens as an async generator."""
        pass

    @abstractmethod
    async def check_health(self) -> Dict[str, Any]:
        """Check provider connectivity and model availability."""
        pass

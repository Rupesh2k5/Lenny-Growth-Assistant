from typing import Dict, Any, Optional
from app.core.config import settings
from app.core.logging import logger
from app.models.provider import BaseLLMProvider
from app.models.ollama_provider import OllamaProvider
from app.models.anthropic_provider import AnthropicProvider
from app.models.openai_provider import OpenAIProvider
from app.models.mock_provider import MockOfflineProvider
from app.infrastructure.llm.cloud import CloudLLMProvider

class LLMProviderFactory:
    _instance: Optional["LLMProviderFactory"] = None
    _active_provider_name: str = settings.DEFAULT_PROVIDER
    _providers: Dict[str, BaseLLMProvider] = {}

    def __init__(self):
        self._initialize_providers()

    @classmethod
    def get_instance(cls) -> "LLMProviderFactory":
        if cls._instance is None:
            cls._instance = LLMProviderFactory()
        return cls._instance

    def _initialize_providers(self):
        # Register all supported providers
        self._providers["ollama"] = OllamaProvider(
            model_name=settings.OLLAMA_MODEL,
            base_url=settings.OLLAMA_BASE_URL
        )
        self._providers["anthropic"] = AnthropicProvider(
            model_name=settings.ANTHROPIC_MODEL,
            api_key=settings.ANTHROPIC_API_KEY
        )
        self._providers["openai"] = OpenAIProvider(
            model_name=settings.OPENAI_MODEL,
            api_key=settings.OPENAI_API_KEY
        )
        self._providers["mock"] = MockOfflineProvider()
        self._providers["cloud"] = CloudLLMProvider()

    def get_provider(self, provider_name: Optional[str] = None) -> BaseLLMProvider:
        name = (provider_name or self._active_provider_name).lower()
        if name in self._providers:
            return self._providers[name]
        logger.warning(f"Unknown provider '{name}'. Falling back to default mock/offline provider.")
        return self._providers["mock"]

    def set_active_provider(self, provider_name: str):
        name = provider_name.lower()
        if name in self._providers:
            self._active_provider_name = name
            logger.info(f"Switched active LLM provider to: {name}")
        else:
            raise ValueError(f"Provider '{provider_name}' is not supported. Choose from: {list(self._providers.keys())}")

    async def get_all_provider_statuses(self) -> Dict[str, Any]:
        statuses = {}
        for name, provider in self._providers.items():
            try:
                health = await provider.check_health()
                statuses[name] = {
                    "is_active": (name == self._active_provider_name),
                    **health
                }
            except Exception as e:
                statuses[name] = {
                    "is_active": (name == self._active_provider_name),
                    "status": "error",
                    "message": str(e)
                }
        return {
            "active_provider": self._active_provider_name,
            "providers": statuses
        }

provider_factory = LLMProviderFactory.get_instance()

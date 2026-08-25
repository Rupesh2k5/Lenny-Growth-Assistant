from typing import Any, Dict, Optional

class AppError(Exception):
    """
    Base domain application exception.
    Converted into standardized JSON error envelopes by the global exception handler.
    """
    code: str = "APPLICATION_ERROR"
    status_code: int = 500
    retryable: bool = False

    def __init__(
        self,
        message: str,
        *,
        details: Optional[Dict[str, Any]] = None,
        code: Optional[str] = None,
        status_code: Optional[int] = None,
        retryable: Optional[bool] = None
    ) -> None:
        super().__init__(message)
        self.message = message
        self.details = details or {}
        if code:
            self.code = code
        if status_code:
            self.status_code = status_code
        if retryable is not None:
            self.retryable = retryable

class ConfigurationError(AppError):
    code = "CONFIGURATION_ERROR"
    status_code = 500
    retryable = False

class ResourceNotFoundError(AppError):
    code = "RESOURCE_NOT_FOUND"
    status_code = 404
    retryable = False

class ValidationAppError(AppError):
    code = "VALIDATION_ERROR"
    status_code = 422
    retryable = False

class RetrievalError(AppError):
    code = "RETRIEVAL_ERROR"
    status_code = 500
    retryable = True

class LLMProviderUnavailable(AppError):
    code = "LLM_PROVIDER_UNAVAILABLE"
    status_code = 503
    retryable = True

class LLMProviderTimeout(AppError):
    code = "LLM_PROVIDER_TIMEOUT"
    status_code = 504
    retryable = True

class UnsafeArtifactError(AppError):
    code = "UNSAFE_ARTIFACT_ERROR"
    status_code = 422
    retryable = False

from typing import Any, Dict, Optional
from pydantic import BaseModel, Field

class ErrorDetail(BaseModel):
    code: str
    message: str
    request_id: Optional[str] = None
    retryable: bool = False
    details: Dict[str, Any] = Field(default_factory=dict)

class ErrorResponse(BaseModel):
    error: ErrorDetail

class StatusResponse(BaseModel):
    status: str
    message: Optional[str] = None

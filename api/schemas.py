from typing import List, Dict, Any, Optional
from pydantic import BaseModel

# Module A Schemas
class ExplanationRequest(BaseModel):
    query: str

class ExplanationResponse(BaseModel):
    summary: str
    key_point: str
    explanation: str
    next_steps: str
    sources: List[Dict[str, Any]]
    query: str

# Module C Schemas
class LetterGenerationRequest(BaseModel):
    description: str
    additional_data: Optional[Dict[str, str]] = None

class LetterGenerationResponse(BaseModel):
    success: bool
    letter: Optional[str] = None
    template_used: Optional[str] = None
    missing_fields: Optional[List[str]] = None
    error: Optional[str] = None
    method: Optional[str] = None

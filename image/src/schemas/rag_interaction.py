from pydantic import BaseModel, Field
from typing import List, Optional
from enum import Enum
from datetime import datetime
from uuid import uuid4


class ResponseType(str, Enum):
    RAG = "RAG"
    FUNCTION_CALL = "FUNCTION_CALL"
    TEXT = "TEXT"  # Add this new type


class RagInteraction(BaseModel):
    interaction_id: str = Field(default_factory=lambda: str(uuid4()))
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    user_id: str
    user_query: str
    response_type: ResponseType
    response_content: str
    sources: Optional[List[str]] = None
    success: bool = True


class RagInteractionCreate(BaseModel):
    user_id: str
    user_query: str
    response_type: ResponseType
    response_content: str
    sources: Optional[List[str]] = None
    success: bool = True

    class Config:
        use_enum_values = True  # This allows passing string values for enums

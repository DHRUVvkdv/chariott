from pydantic import BaseModel, HttpUrl
from typing import Optional


class DocumentUploadResponse(BaseModel):
    chain_id: str
    hotel_id: Optional[str]
    document_name: str
    url: HttpUrl
    user_id: str
    processing_status: str = "completed"


class DocumentUploadError(BaseModel):
    error: str

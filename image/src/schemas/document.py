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


class DocumentListResponse(BaseModel):
    file_name: str
    status: str
    s3_url: HttpUrl
    user_id: str


class DocumentResponse(DocumentListResponse):
    chain_id: Optional[str] = None
    hotel_id: Optional[str] = None

import logging
from fastapi import (
    APIRouter,
    UploadFile,
    File,
    HTTPException,
    Form,
    Depends,
    Request,
    Query,
)
from typing import List
from services.s3_service import upload_file_to_s3
from services.document_processor import process_document
from services.dynamodb_service import (
    get_all_documents,
    get_documents_by_user_id,
    get_document_by_id,
    delete_document,
)
from schemas.document import (
    DocumentUploadResponse,
    DocumentUploadError,
    DocumentListResponse,
    DocumentResponse,
)
from schemas.user import User
from middleware.auth import get_current_user

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post(
    "/upload",
    response_model=DocumentUploadResponse,
    responses={400: {"model": DocumentUploadError}},
)
async def upload_document(
    request: Request,
    file: UploadFile = File(...),
    chain_id: str = Form(...),
    hotel_id: str = Form(None),
    current_user: User = Depends(get_current_user),
):
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are allowed")

    result = await upload_file_to_s3(file, chain_id, hotel_id)

    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])

    document_id = (
        f"{chain_id}_{hotel_id}_{file.filename}"
        if hotel_id
        else f"{chain_id}_{file.filename}"
    )

    # Process document synchronously
    await process_document(document_id, result["url"], current_user.user_id)

    return DocumentUploadResponse(
        chain_id=chain_id,
        hotel_id=hotel_id,
        document_name=file.filename,
        url=result["url"],
        user_id=current_user.user_id,
        processing_status="completed",
    )


@router.get("/documents", response_model=List[DocumentListResponse])
async def list_documents(
    current_user: User = Depends(get_current_user),
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
):
    documents = await get_all_documents(skip, limit)
    return [DocumentListResponse(**doc) for doc in documents]


@router.get("/documents/user", response_model=List[DocumentListResponse])
async def list_user_documents(
    current_user: User = Depends(get_current_user),
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
):
    documents = await get_documents_by_user_id(current_user.user_id, skip, limit)
    return [DocumentListResponse(**doc) for doc in documents]


@router.get("/documents/{document_id}", response_model=DocumentResponse)
async def get_document(
    document_id: str, current_user: User = Depends(get_current_user)
):
    document = await get_document_by_id(document_id)
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    return DocumentResponse(**document)


@router.delete("/documents/{document_id}", status_code=204)
async def delete_document_endpoint(
    document_id: str, current_user: User = Depends(get_current_user)
):
    document = await get_document_by_id(document_id)
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    if document["user_id"] != current_user.user_id:
        raise HTTPException(
            status_code=403, detail="Not authorized to delete this document"
        )
    await delete_document(document_id)
    return None

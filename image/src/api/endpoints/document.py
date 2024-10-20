import logging
from fastapi import APIRouter, UploadFile, File, HTTPException, Form, Depends, Request
from services.s3_service import upload_file_to_s3
from services.document_processor import process_document
from schemas.document import DocumentUploadResponse, DocumentUploadError
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

from fastapi import APIRouter, UploadFile, File, HTTPException, Form
from services.s3_service import upload_file_to_s3, create_folder_if_not_exists
from schemas.document import DocumentUploadResponse, DocumentUploadError

router = APIRouter()


@router.post(
    "/upload",
    response_model=DocumentUploadResponse,
    responses={400: {"model": DocumentUploadError}},
)
async def upload_document(
    file: UploadFile = File(...), chain_id: str = Form(...), hotel_id: str = Form(None)
):
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are allowed")

    # Ensure the chain folder exists
    if not await create_folder_if_not_exists(chain_id):
        raise HTTPException(
            status_code=500, detail=f"Failed to create chain folder '{chain_id}'"
        )

    # If hotel_id is provided, ensure the hotel folder exists
    if hotel_id:
        hotel_path = f"{chain_id}/{hotel_id}"
        if not await create_folder_if_not_exists(hotel_path):
            raise HTTPException(
                status_code=500,
                detail=f"Failed to create hotel folder '{hotel_id}' in chain '{chain_id}'",
            )

    result = await upload_file_to_s3(file, chain_id, hotel_id)

    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])

    return result

from fastapi import APIRouter, HTTPException, Depends
from typing import Dict
from schemas.user import User
from middleware.auth import get_current_user
from services.pinecone_service import delete_document_vectors

router = APIRouter()


@router.delete("/vectors/{document_id}", status_code=200, response_model=Dict[str, str])
async def delete_document_vectors_endpoint(
    document_id: str, current_user: User = Depends(get_current_user)
):
    try:
        delete_response = await delete_document_vectors(document_id)
        return {"message": delete_response}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting vectors: {str(e)}")

from fastapi import APIRouter, Depends, HTTPException, Query
from schemas.request import (
    RequestCreate,
    RequestUpdate,
    RequestResponse,
    RequestStatus,
)
from services.request_service import RequestService
from middleware.auth import get_current_user
from schemas.user import User
from typing import List, Optional

router = APIRouter()


@router.post("/requests", response_model=RequestResponse)
async def create_request(
    request: RequestCreate,
    current_user: User = Depends(get_current_user),
    request_service: RequestService = Depends(),
):
    return await request_service.create_request(request)


@router.get("/requests/{request_id}", response_model=RequestResponse)
async def get_request(
    request_id: str,
    current_user: User = Depends(get_current_user),
    request_service: RequestService = Depends(),
):
    request = await request_service.get_request(request_id)
    if not request:
        raise HTTPException(status_code=404, detail="Request not found")
    return request


@router.put("/requests/{request_id}", response_model=RequestResponse)
async def update_request(
    request_id: str,
    update: RequestUpdate,
    current_user: User = Depends(get_current_user),
    request_service: RequestService = Depends(),
):
    request = await request_service.update_request(request_id, update)
    if not request:
        raise HTTPException(status_code=404, detail="Request not found")
    return request


@router.get("/requests/hotel/{hotel_id}", response_model=List[RequestResponse])
async def get_requests_by_hotel(
    hotel_id: str,
    status: RequestStatus = None,
    current_user: User = Depends(get_current_user),
    request_service: RequestService = Depends(),
):
    return await request_service.get_requests_by_hotel(hotel_id, status)


@router.get("/requests/user/{user_id}", response_model=List[RequestResponse])
async def get_requests_by_user(
    user_id: str,
    status: RequestStatus = None,
    current_user: User = Depends(get_current_user),
    request_service: RequestService = Depends(),
):
    return await request_service.get_requests_by_user(user_id, status)


@router.get("/all", response_model=dict)
async def get_all_requests(
    status: Optional[RequestStatus] = None,
    limit: int = Query(50, ge=1, le=100),
    last_evaluated_key: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    request_service: RequestService = Depends(),
):
    return await request_service.get_all_requests(status, limit, last_evaluated_key)


@router.get("/all_status", response_model=dict)
async def get_all_requests_all_status(
    limit: int = Query(50, ge=1, le=100),
    last_evaluated_key: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    request_service: RequestService = Depends(),
):
    return await request_service.get_all_requests(None, limit, last_evaluated_key)

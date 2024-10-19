from fastapi import APIRouter, HTTPException
from schemas.user import UserCreate, UserLogin
from services.user_service import UserService

router = APIRouter()


@router.post("/register")
async def register_user(user: UserCreate):
    return await UserService.create_user(user)


@router.post("/login")
async def login_user(user: UserLogin):
    return await UserService.login_user(user)

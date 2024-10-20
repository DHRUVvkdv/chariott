from fastapi import APIRouter, HTTPException
from schemas.user import UserCreate, UserLogin, UserInDB
from services.user_service import UserService
from typing import List

router = APIRouter()


@router.post("/register")
async def register_user(user: UserCreate):
    return await UserService.create_user(user)


@router.post("/login")
async def login_user(user: UserLogin):
    return await UserService.login_user(user)


@router.get("/users", response_model=List[UserInDB])
async def get_all_users():
    return await UserService.get_all_users()


@router.delete("/users/{user_id}")
async def delete_user(user_id: str):
    return await UserService.delete_user(user_id)

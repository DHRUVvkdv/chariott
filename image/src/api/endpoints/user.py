from fastapi import APIRouter, HTTPException, Depends
from schemas.user import UserCreate, UserLogin, UserInDB, Preferences
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
    users = await UserService.get_all_users()
    for user in users:
        await UserService.increment_interaction_counter(user.user_id)
    return users


@router.get("/user/{user_id}", response_model=UserInDB)
async def get_user(user_id: str):
    user = await UserService.get_user(user_id)
    await UserService.increment_interaction_counter(user_id)
    return user


@router.delete("/users/{user_id}")
async def delete_user(user_id: str):
    return await UserService.delete_user(user_id)


@router.get("/allstaff", response_model=List[UserInDB])
async def get_all_staff():
    return await UserService.get_all_staff()


@router.get("/allnormal", response_model=List[UserInDB])
async def get_all_normal():
    return await UserService.get_all_normal()


@router.put("/users/{user_id}/preferences")
async def update_preferences(user_id: str, preferences: Preferences):
    return await UserService.update_preferences(user_id, preferences)


@router.get("/users/{user_id}/preferences", response_model=Preferences)
async def get_preferences(user_id: str):
    return await UserService.get_preferences(user_id)


@router.get("/users/{user_id}/interaction-counter")
async def get_interaction_counter(user_id: str):
    return {"interaction_counter": await UserService.get_interaction_counter(user_id)}

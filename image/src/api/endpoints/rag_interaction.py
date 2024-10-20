from fastapi import APIRouter, Depends, HTTPException
from typing import List
from schemas.rag_interaction import RagInteraction, RagInteractionCreate
from services.rag_interaction_service import RagInteractionService

router = APIRouter()


@router.post("/interactions", response_model=RagInteraction)
async def create_interaction(interaction: RagInteractionCreate):
    return await RagInteractionService.create_interaction(interaction)


@router.get("/interactions/{interaction_id}", response_model=RagInteraction)
async def get_interaction(interaction_id: str):
    return await RagInteractionService.get_interaction(interaction_id)


@router.get("/interactions/user/{user_id}", response_model=List[RagInteraction])
async def get_interactions_by_user(user_id: str):
    return await RagInteractionService.get_interactions_by_user(user_id)

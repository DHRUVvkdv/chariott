# api/endpoints/top_user_recommendations.py

from fastapi import APIRouter, Depends
from typing import List
from services.agent_manager import AgentManager, get_agent_manager
from schemas.top_user_recommendations import (
    TopUserRecommendationsRequest,
    TopUserRecommendationsResponse,
    UserInteractionsAnalysisRequest,
    UserInteractionsAnalysisResponse,
)

router = APIRouter()


@router.post("/top_user_recommendations", response_model=TopUserRecommendationsResponse)
async def get_top_user_recommendations(
    request: TopUserRecommendationsRequest,
    agent_manager: AgentManager = Depends(get_agent_manager),
):
    recommendations = agent_manager.process_request(
        "top_user_recommendations", request.user_query
    )
    return TopUserRecommendationsResponse(recommendations=recommendations)


@router.post(
    "/analyze_user_interactions", response_model=UserInteractionsAnalysisResponse
)
async def analyze_user_interactions(
    request: UserInteractionsAnalysisRequest,
    agent_manager: AgentManager = Depends(get_agent_manager),
):
    analysis = agent_manager.process_request(
        "analyze_user_interactions", request.user_interactions
    )
    return UserInteractionsAnalysisResponse(analysis=analysis)

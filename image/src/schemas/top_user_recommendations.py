from pydantic import BaseModel
from typing import List


class TopUserRecommendationsRequest(BaseModel):
    user_query: str

    class Config:
        schema_extra = {
            "example": {"user_query": "I'm looking for a beachfront hotel with a spa"}
        }


class TopUserRecommendationsResponse(BaseModel):
    recommendations: str

    class Config:
        schema_extra = {
            "example": {
                "recommendations": "Based on your query, here are the top recommendations: 1. Seaside Luxury Resort & Spa: This 5-star hotel offers stunning ocean views, a world-class spa, and direct beach access. 2. Oceanfront Wellness Retreat: Known for its holistic spa treatments and private beach area. 3. Coastal Paradise Hotel: Features a beachfront location, multiple pools, and a full-service spa."
            }
        }


class UserInteraction(BaseModel):
    interaction_type: str
    content: str

    class Config:
        schema_extra = {
            "example": {
                "interaction_type": "search",
                "content": "family-friendly resorts with kids club",
            }
        }


class UserInteractionsAnalysisRequest(BaseModel):
    user_interactions: List[UserInteraction]

    class Config:
        schema_extra = {
            "example": {
                "user_interactions": [
                    {
                        "interaction_type": "search",
                        "content": "family-friendly resorts with kids club",
                    },
                    {
                        "interaction_type": "booking",
                        "content": "Sunnyville Family Resort",
                    },
                    {
                        "interaction_type": "review",
                        "content": "Great experience, kids loved the activities",
                    },
                ]
            }
        }


class UserInteractionsAnalysisResponse(BaseModel):
    analysis: str

    class Config:
        schema_extra = {
            "example": {
                "analysis": "Based on the user interactions analysis, we can conclude that this user is primarily interested in family-friendly accommodations. They consistently search for and book resorts that cater to families, particularly those with dedicated facilities for children such as kids clubs. Their positive reviews emphasize the importance of activities for children. Recommendations for improving user engagement include: 1. Highlight family-oriented features in search results and listings. 2. Offer personalized recommendations for family-friendly resorts. 3. Implement a loyalty program that rewards bookings at family-friendly properties."
            }
        }

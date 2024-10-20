import boto3
from botocore.exceptions import ClientError
from fastapi import HTTPException
from core.config import settings
from schemas.rag_interaction import RagInteraction, RagInteractionCreate
from typing import List
from datetime import datetime

dynamodb = boto3.resource("dynamodb", region_name=settings.PRIVATE_AWS_REGION)
table = dynamodb.Table(settings.DYNAMODB_TABLE_NAME_RAG_INTERACTIONS)


class RagInteractionService:
    @staticmethod
    async def create_interaction(interaction: RagInteractionCreate) -> RagInteraction:
        rag_interaction = RagInteraction(**interaction.dict())
        item = rag_interaction.dict()
        item["timestamp"] = item["timestamp"].isoformat()

        try:
            table.put_item(Item=item)
            return rag_interaction
        except ClientError as e:
            raise HTTPException(status_code=500, detail=str(e))

    @staticmethod
    async def get_interaction(interaction_id: str) -> RagInteraction:
        try:
            response = table.get_item(Key={"interaction_id": interaction_id})
            item = response.get("Item")
            if not item:
                raise HTTPException(status_code=404, detail="Interaction not found")
            item["timestamp"] = datetime.fromisoformat(item["timestamp"])
            return RagInteraction(**item)
        except ClientError as e:
            raise HTTPException(status_code=500, detail=str(e))

    @staticmethod
    async def get_interactions_by_user(user_id: str) -> List[RagInteraction]:
        try:
            response = table.query(
                IndexName="user_id-index",
                KeyConditionExpression="user_id = :user_id",
                ExpressionAttributeValues={":user_id": user_id},
            )
            items = response.get("Items", [])
            for item in items:
                item["timestamp"] = datetime.fromisoformat(item["timestamp"])
            return [RagInteraction(**item) for item in items]
        except ClientError as e:
            raise HTTPException(status_code=500, detail=str(e))

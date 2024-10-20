import boto3
from botocore.exceptions import ClientError
from fastapi import HTTPException
from core.config import settings
from schemas.hotel import HotelCreate, HotelUpdate, Hotel, CommunityProject
from uuid import uuid4
from typing import List, Dict, Any

dynamodb = boto3.resource("dynamodb", region_name=settings.PRIVATE_AWS_REGION)
table = dynamodb.Table(settings.DYNAMODB_TABLE_NAME_HOTELS)


class HotelService:
    @staticmethod
    def _serialize_hotel(hotel: Dict[str, Any]) -> Dict[str, Any]:
        if "local_community_projects" in hotel:
            hotel["local_community_projects"] = [
                {**project, "image_url": str(project["image_url"])}
                for project in hotel["local_community_projects"]
            ]
        return hotel

    @staticmethod
    def _deserialize_hotel(hotel: Dict[str, Any]) -> Dict[str, Any]:
        if "local_community_projects" in hotel:
            hotel["local_community_projects"] = [
                CommunityProject(**project)
                for project in hotel["local_community_projects"]
            ]
        return hotel

    @staticmethod
    async def create_hotel(hotel: HotelCreate):
        hotel_id = str(uuid4())
        item = HotelService._serialize_hotel({"hotel_id": hotel_id, **hotel.dict()})
        try:
            table.put_item(Item=item)
            return Hotel(**HotelService._deserialize_hotel(item))
        except ClientError as e:
            raise HTTPException(status_code=500, detail=str(e))

    @staticmethod
    async def get_hotel(hotel_id: str):
        try:
            response = table.get_item(Key={"hotel_id": hotel_id})
            item = response.get("Item")
            if not item:
                raise HTTPException(status_code=404, detail="Hotel not found")
            return Hotel(**HotelService._deserialize_hotel(item))
        except ClientError as e:
            raise HTTPException(status_code=500, detail=str(e))

    @staticmethod
    async def update_hotel(hotel_id: str, hotel_update: HotelUpdate):
        update_expression = "SET "
        expression_attribute_values = {}
        expression_attribute_names = {}

        update_data = hotel_update.dict(exclude_unset=True)
        serialized_data = HotelService._serialize_hotel(update_data)

        for field, value in serialized_data.items():
            if value is not None:
                update_expression += f"#{field} = :{field}, "
                expression_attribute_values[f":{field}"] = value
                expression_attribute_names[f"#{field}"] = field

        update_expression = update_expression.rstrip(", ")

        try:
            response = table.update_item(
                Key={"hotel_id": hotel_id},
                UpdateExpression=update_expression,
                ExpressionAttributeValues=expression_attribute_values,
                ExpressionAttributeNames=expression_attribute_names,
                ReturnValues="ALL_NEW",
            )
            updated_item = response.get("Attributes", {})
            return Hotel(**HotelService._deserialize_hotel(updated_item))
        except ClientError as e:
            raise HTTPException(status_code=500, detail=str(e))

    @staticmethod
    async def get_all_hotels() -> List[Hotel]:
        try:
            response = table.scan()
            items = response.get("Items", [])
            return [Hotel(**HotelService._deserialize_hotel(item)) for item in items]
        except ClientError as e:
            raise HTTPException(status_code=500, detail=str(e))

    @staticmethod
    async def delete_hotel(hotel_id: str):
        try:
            table.delete_item(Key={"hotel_id": hotel_id})
            return {"message": "Hotel deleted successfully"}
        except ClientError as e:
            raise HTTPException(status_code=500, detail=str(e))

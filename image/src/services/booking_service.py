import boto3
from botocore.exceptions import ClientError
from fastapi import HTTPException
from core.config import settings
from schemas.booking import BookingCreate, BookingUpdate
from utils.utils import get_current_est_time, format_est_datetime, parse_est_datetime
from uuid import uuid4
from datetime import datetime
from typing import List

dynamodb = boto3.resource("dynamodb", region_name=settings.PRIVATE_AWS_REGION)
table = dynamodb.Table(settings.DYNAMODB_TABLE_NAME_BOOKINGS)


class BookingService:
    @staticmethod
    async def create_booking(booking: BookingCreate):
        booking_id = str(uuid4())
        item = {
            "booking_id": booking_id,
            **booking.dict(),
            "start_date": format_est_datetime(booking.start_date),
            "end_date": format_est_datetime(booking.end_date),
        }
        try:
            table.put_item(Item=item)
            return {"booking_id": booking_id, **item}
        except ClientError as e:
            raise HTTPException(status_code=500, detail=str(e))

    @staticmethod
    async def get_booking(booking_id: str):
        try:
            response = table.get_item(Key={"booking_id": booking_id})
            item = response.get("Item")
            if not item:
                raise HTTPException(status_code=404, detail="Booking not found")
            # Convert string dates back to datetime objects
            item["start_date"] = parse_est_datetime(item["start_date"])
            item["end_date"] = parse_est_datetime(item["end_date"])
            return item
        except ClientError as e:
            raise HTTPException(status_code=500, detail=str(e))

    @staticmethod
    async def get_all_bookings():
        try:
            response = table.scan()
            return response.get("Items", [])
        except ClientError as e:
            raise HTTPException(status_code=500, detail=str(e))

    @staticmethod
    async def get_current_bookings(user_id: str):
        current_time = get_current_est_time()
        try:
            response = table.scan(
                FilterExpression="user_id = :user_id AND :current_time BETWEEN start_date AND end_date",
                ExpressionAttributeValues={
                    ":user_id": user_id,
                    ":current_time": format_est_datetime(current_time),
                },
            )
            return response.get("Items", [])
        except ClientError as e:
            raise HTTPException(status_code=500, detail=str(e))

    @staticmethod
    async def get_past_bookings(user_id: str):
        current_time = get_current_est_time()
        try:
            response = table.scan(
                FilterExpression="user_id = :user_id AND end_date < :current_time",
                ExpressionAttributeValues={
                    ":user_id": user_id,
                    ":current_time": format_est_datetime(current_time),
                },
            )
            return response.get("Items", [])
        except ClientError as e:
            raise HTTPException(status_code=500, detail=str(e))

    @staticmethod
    async def get_future_bookings(user_id: str):
        current_time = get_current_est_time()
        try:
            response = table.scan(
                FilterExpression="user_id = :user_id AND start_date > :current_time",
                ExpressionAttributeValues={
                    ":user_id": user_id,
                    ":current_time": format_est_datetime(current_time),
                },
            )
            return response.get("Items", [])
        except ClientError as e:
            raise HTTPException(status_code=500, detail=str(e))

    @staticmethod
    async def update_booking(booking_id: str, booking_update: BookingUpdate):
        update_expression = "SET "
        expression_attribute_values = {}
        expression_attribute_names = {}

        for field, value in booking_update.dict(exclude_unset=True).items():
            update_expression += f"#{field} = :{field}, "
            if isinstance(value, datetime):
                expression_attribute_values[f":{field}"] = format_est_datetime(value)
            else:
                expression_attribute_values[f":{field}"] = value
            expression_attribute_names[f"#{field}"] = field

        update_expression = update_expression.rstrip(", ")

        try:
            response = table.update_item(
                Key={"booking_id": booking_id},
                UpdateExpression=update_expression,
                ExpressionAttributeValues=expression_attribute_values,
                ExpressionAttributeNames=expression_attribute_names,
                ReturnValues="ALL_NEW",
            )
            updated_item = response.get("Attributes", {})
            # Convert string dates back to datetime objects
            if "start_date" in updated_item:
                updated_item["start_date"] = parse_est_datetime(
                    updated_item["start_date"]
                )
            if "end_date" in updated_item:
                updated_item["end_date"] = parse_est_datetime(updated_item["end_date"])
            return updated_item
        except ClientError as e:
            raise HTTPException(status_code=500, detail=str(e))

    @staticmethod
    async def delete_booking(booking_id: str):
        try:
            table.delete_item(Key={"booking_id": booking_id})
            return {"message": "Booking deleted successfully"}
        except ClientError as e:
            raise HTTPException(status_code=500, detail=str(e))

    @staticmethod
    async def get_all_bookings() -> List[dict]:
        try:
            response = table.scan()
            items = response.get("Items", [])

            # Convert string dates back to datetime objects for all items
            for item in items:
                if "start_date" in item:
                    item["start_date"] = parse_est_datetime(item["start_date"])
                if "end_date" in item:
                    item["end_date"] = parse_est_datetime(item["end_date"])

            return items
        except ClientError as e:
            raise HTTPException(status_code=500, detail=str(e))

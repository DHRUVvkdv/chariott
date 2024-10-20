import boto3
from boto3.dynamodb.conditions import Key
from datetime import datetime
from uuid import uuid4
from core.config import settings
from schemas.request import (
    Request,
    RequestCreate,
    RequestUpdate,
    RequestStatus,
    RequestResponse,
)
from utils.utils import get_current_est_time
import json
from typing import List, Optional


class RequestService:
    def __init__(self):
        self.dynamodb = boto3.resource(
            "dynamodb", region_name=settings.PRIVATE_AWS_REGION
        )
        self.table = self.dynamodb.Table(settings.DYNAMODB_TABLE_NAME_REQUESTS)

    async def create_request(self, request: RequestCreate) -> RequestResponse:
        request_id = str(uuid4())
        now = get_current_est_time()
        item = {
            "request_id": request_id,
            "user_id": request.user_id,
            "hotel_id": request.hotel_id,
            "department": request.department.value,
            "task": request.task,
            "time_issued": now.isoformat(),
            "status": RequestStatus.PENDING.value,
        }
        self.table.put_item(Item=item)
        return RequestResponse(**item)

    async def get_request(self, request_id: str) -> RequestResponse:
        response = self.table.get_item(Key={"request_id": request_id})
        item = response.get("Item")
        if item:
            return RequestResponse(**item)
        return None

    async def update_request(
        self, request_id: str, update: RequestUpdate
    ) -> RequestResponse:
        update_expression = "SET #status = :status"
        expression_attribute_names = {"#status": "status"}
        expression_attribute_values = {":status": update.status.value}

        if update.status == RequestStatus.COMPLETED:
            update_expression += ", time_completed = :time_completed"
            expression_attribute_values[":time_completed"] = (
                get_current_est_time().isoformat()
            )

        response = self.table.update_item(
            Key={"request_id": request_id},
            UpdateExpression=update_expression,
            ExpressionAttributeNames=expression_attribute_names,
            ExpressionAttributeValues=expression_attribute_values,
            ReturnValues="ALL_NEW",
        )
        return RequestResponse(**response["Attributes"])

    async def get_requests_by_hotel(
        self, hotel_id: str, status: RequestStatus = None
    ) -> list[RequestResponse]:
        key_condition = Key("hotel_id").eq(hotel_id)
        if status:
            key_condition &= Key("status").eq(status.value)

        query_params = {
            "IndexName": "hotel_id-status-index",
            "KeyConditionExpression": key_condition,
        }

        response = self.table.query(**query_params)
        return [RequestResponse(**item) for item in response["Items"]]

    async def get_requests_by_user(
        self, user_id: str, status: RequestStatus = None
    ) -> list[RequestResponse]:
        key_condition = Key("user_id").eq(user_id)
        if status:
            key_condition &= Key("status").eq(status.value)

        query_params = {
            "IndexName": "user_id-status-index",
            "KeyConditionExpression": key_condition,
        }

        response = self.table.query(**query_params)
        return [RequestResponse(**item) for item in response["Items"]]

    async def get_all_requests(
        self,
        status: Optional[RequestStatus] = None,
        limit: int = 50,
        last_evaluated_key: Optional[str] = None,
    ) -> dict:
        scan_kwargs = {"Limit": limit}

        if status:
            scan_kwargs["FilterExpression"] = Key("status").eq(status.value)

        if last_evaluated_key:
            scan_kwargs["ExclusiveStartKey"] = json.loads(last_evaluated_key)

        response = self.table.scan(**scan_kwargs)

        items = response.get("Items", [])
        last_key = response.get("LastEvaluatedKey")

        requests = [RequestResponse(**item) for item in items]

        return {
            "requests": requests,
            "last_evaluated_key": json.dumps(last_key) if last_key else None,
        }

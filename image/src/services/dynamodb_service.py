import boto3
from core.config import settings
from boto3.dynamodb.conditions import Key

dynamodb = boto3.resource("dynamodb", region_name=settings.PRIVATE_AWS_REGION)
table = dynamodb.Table(settings.DYNAMODB_TABLE_NAME_PROCESSED_FILES)


async def update_document_status(
    document_id: str, status: str, s3_url: str, user_id: str
):
    table.put_item(
        Item={
            "file_name": document_id,
            "status": status,
            "s3_url": s3_url,
            "user_id": user_id,
        }
    )


async def get_all_documents(skip: int = 0, limit: int = 10):
    scan_kwargs = {"Limit": limit}

    if skip > 0:
        # Perform a scan operation to get the item at the 'skip' position
        response = table.scan(
            Limit=1,
            Select="ALL_ATTRIBUTES",
            ExclusiveStartKey={"file_name": f"item_{skip}"},
        )
        last_evaluated_key = response.get("LastEvaluatedKey")

        if last_evaluated_key:
            scan_kwargs["ExclusiveStartKey"] = last_evaluated_key

    response = table.scan(**scan_kwargs)
    return response.get("Items", [])


async def get_documents_by_user_id(user_id: str, skip: int = 0, limit: int = 10):
    scan_kwargs = {"FilterExpression": Key("user_id").eq(user_id), "Limit": limit}

    if skip > 0:
        # Perform initial scans to skip items
        for _ in range(0, skip, limit):
            response = table.scan(**scan_kwargs)
            if "LastEvaluatedKey" not in response:
                return []  # No more items to skip
            scan_kwargs["ExclusiveStartKey"] = response["LastEvaluatedKey"]

    response = table.scan(**scan_kwargs)
    return response.get("Items", [])


async def get_document_by_id(document_id: str):
    response = table.get_item(Key={"file_name": document_id})
    item = response.get("Item")
    if item:
        # Parse chain_id and hotel_id from document_id
        parts = document_id.split("_", 2)
        chain_id = parts[0] if len(parts) > 0 else None
        hotel_id = parts[1] if len(parts) > 1 else None
        item["chain_id"] = chain_id
        item["hotel_id"] = hotel_id
    return item


async def delete_document(document_id: str):
    table.delete_item(Key={"file_name": document_id})

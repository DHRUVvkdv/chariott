import boto3
from core.config import settings

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

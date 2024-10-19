import boto3
from core.config import settings


def get_s3_client():
    return boto3.client(
        "s3",
        aws_access_key_id=settings.PRIVATE_AWS_ACCESS_KEY_ID,
        aws_secret_access_key=settings.PRIVATE_AWS_SECRET_ACCESS_KEY,
        region_name=settings.PRIVATE_AWS_REGION,
    )

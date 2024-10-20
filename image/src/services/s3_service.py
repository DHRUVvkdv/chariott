import boto3
from fastapi import UploadFile
from core.config import settings
import io

s3_client = boto3.client(
    "s3",
    aws_access_key_id=settings.PRIVATE_AWS_ACCESS_KEY_ID,
    aws_secret_access_key=settings.PRIVATE_AWS_SECRET_ACCESS_KEY,
    region_name=settings.PRIVATE_AWS_REGION,
)


async def upload_file_to_s3(file: UploadFile, chain_id: str, hotel_id: str = None):
    if hotel_id:
        key = f"{chain_id}/{hotel_id}/{file.filename}"
    else:
        key = f"{chain_id}/{file.filename}"

    try:
        s3_client.upload_fileobj(file.file, settings.S3_BUCKET_NAME, key)
        url = f"https://{settings.S3_BUCKET_NAME}.s3.amazonaws.com/{key}"
        return {
            "chain_id": chain_id,
            "hotel_id": hotel_id,
            "document_name": file.filename,
            "url": url,
        }
    except Exception as e:
        return {"error": str(e)}


async def get_file_from_s3(s3_url: str):
    bucket_name = s3_url.split("//")[1].split(".")[0]
    key = "/".join(s3_url.split("/")[3:])

    response = s3_client.get_object(Bucket=bucket_name, Key=key)
    return io.BytesIO(response["Body"].read())

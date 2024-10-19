from core.s3_client import get_s3_client
from core.config import settings
from fastapi import UploadFile

# Note: I am creating a folder if it does not exist in the S3 bucket, we need to make sure the user is authenticated before creating the folder, and they exist in the Hotels/Chains database.


async def upload_file_to_s3(file: UploadFile, chain_id: str, hotel_id: str = None):
    s3_client = get_s3_client()

    if hotel_id:
        key = f"{chain_id}/{hotel_id}/{file.filename}"
    else:
        key = f"{chain_id}/{file.filename}"

    try:
        # Ensure the folder structure exists (this is a no-op if it already exists)
        folder_path = key.rsplit("/", 1)[0] + "/"
        s3_client.put_object(Bucket=settings.S3_BUCKET_NAME, Key=folder_path)

        # Upload the file
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


async def check_folder_exists(folder_path: str):
    s3_client = get_s3_client()

    try:
        response = s3_client.list_objects_v2(
            Bucket=settings.S3_BUCKET_NAME, Prefix=folder_path, MaxKeys=1
        )
        return "Contents" in response
    except Exception as e:
        return False


async def create_folder_if_not_exists(folder_path: str):
    s3_client = get_s3_client()

    if not await check_folder_exists(folder_path):
        try:
            s3_client.put_object(
                Bucket=settings.S3_BUCKET_NAME, Key=(folder_path + "/")
            )
            return True
        except Exception as e:
            return False
    return True

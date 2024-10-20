import boto3
from botocore.exceptions import ClientError
from fastapi import HTTPException
from core.config import settings
from schemas.user import (
    UserCreate,
    UserLogin,
    UserType,
    StaffType,
    UserInDB,
    Preferences,
)
from typing import List


class UserService:
    @staticmethod
    async def create_user(user: UserCreate):
        cognito_client = boto3.client(
            "cognito-idp",
            region_name=settings.PRIVATE_AWS_REGION,
        )
        dynamodb = boto3.resource("dynamodb", region_name=settings.PRIVATE_AWS_REGION)
        users_table = dynamodb.Table(settings.DYNAMODB_TABLE_NAME_USERS)

        try:
            # Create user in Cognito
            cognito_response = cognito_client.admin_create_user(
                UserPoolId=settings.COGNITO_USER_POOL_ID,
                Username=user.email,  # Using email as the username
                UserAttributes=[
                    {"Name": "email", "Value": user.email},
                    {"Name": "email_verified", "Value": "true"},
                    {"Name": "given_name", "Value": user.first_name},
                    {"Name": "family_name", "Value": user.last_name},
                    {"Name": "custom:user_type", "Value": user.user_type.value},
                ]
                + (
                    [{"Name": "custom:staff-type", "Value": user.staff_type.value}]
                    if user.staff_type
                    else []
                ),
                TemporaryPassword=user.password,
            )

            # Set the password as permanent
            cognito_client.admin_set_user_password(
                UserPoolId=settings.COGNITO_USER_POOL_ID,
                Username=user.email,
                Password=user.password,
                Permanent=True,
            )

            # Create user entry in DynamoDB
            dynamodb_item = user.dict(exclude={"password"})
            dynamodb_item["user_id"] = user.email  # Use email as user_id
            dynamodb_item["interaction_counter"] = 0
            if user.user_type == UserType.STAFF:
                dynamodb_item["staff_type"] = user.staff_type.value

            dynamodb_response = users_table.put_item(Item=dynamodb_item)

            return {
                "cognito_response": cognito_response,
                "dynamodb_response": dynamodb_response,
            }
        except ClientError as e:
            # Handle errors (e.g., user already exists)
            raise HTTPException(status_code=400, detail=str(e))

    @staticmethod
    async def login_user(user: UserLogin):
        result = await UserService._original_login_user(user)
        await UserService.increment_interaction_counter(user.email)
        return result

    @staticmethod
    async def _original_login_user(user: UserLogin):
        cognito_client = boto3.client(
            "cognito-idp",
            region_name=settings.PRIVATE_AWS_REGION,
        )
        try:
            response = cognito_client.admin_initiate_auth(
                UserPoolId=settings.COGNITO_USER_POOL_ID,
                ClientId=settings.COGNITO_APP_CLIENT_ID,
                AuthFlow="ADMIN_NO_SRP_AUTH",
                AuthParameters={"USERNAME": user.email, "PASSWORD": user.password},
            )
            return {"access_token": response["AuthenticationResult"]["AccessToken"]}
        except ClientError as e:
            raise HTTPException(status_code=401, detail="Invalid credentials")

    import boto3

    @staticmethod
    async def get_all_users() -> List[UserInDB]:
        dynamodb = boto3.resource("dynamodb", region_name=settings.PRIVATE_AWS_REGION)
        users_table = dynamodb.Table(settings.DYNAMODB_TABLE_NAME_USERS)

        try:
            response = users_table.scan()
            users = response.get("Items", [])
            return [UserInDB(**user) for user in users]
        except ClientError as e:
            raise HTTPException(status_code=500, detail=str(e))

    @staticmethod
    async def delete_user(user_id: str):
        cognito_client = boto3.client(
            "cognito-idp",
            region_name=settings.PRIVATE_AWS_REGION,
        )
        dynamodb = boto3.resource("dynamodb", region_name=settings.PRIVATE_AWS_REGION)
        users_table = dynamodb.Table(settings.DYNAMODB_TABLE_NAME_USERS)

        cognito_deleted = False
        dynamodb_deleted = False

        try:
            # Try to delete user from Cognito
            cognito_client.admin_delete_user(
                UserPoolId=settings.COGNITO_USER_POOL_ID, Username=user_id
            )
            cognito_deleted = True
        except ClientError as e:
            if e.response["Error"]["Code"] != "UserNotFoundException":
                raise HTTPException(status_code=400, detail=str(e))

        try:
            # Try to delete user from DynamoDB
            dynamodb_response = users_table.delete_item(
                Key={"user_id": user_id}, ReturnValues="ALL_OLD"
            )
            if "Attributes" in dynamodb_response:
                dynamodb_deleted = True
        except ClientError as e:
            raise HTTPException(status_code=400, detail=str(e))

        if cognito_deleted or dynamodb_deleted:
            return {"message": f"User {user_id} deleted successfully"}
        else:
            raise HTTPException(
                status_code=404, detail="User not found in either Cognito or DynamoDB"
            )

    @staticmethod
    async def get_user(user_id: str) -> UserInDB:
        dynamodb = boto3.resource("dynamodb", region_name=settings.PRIVATE_AWS_REGION)
        users_table = dynamodb.Table(settings.DYNAMODB_TABLE_NAME_USERS)

        try:
            response = users_table.get_item(Key={"user_id": user_id})
            user = response.get("Item")
            if not user:
                raise HTTPException(status_code=404, detail="User not found")
            return UserInDB(**user)
        except ClientError as e:
            raise HTTPException(status_code=500, detail=str(e))

    @staticmethod
    async def get_all_staff() -> List[UserInDB]:
        dynamodb = boto3.resource("dynamodb", region_name=settings.PRIVATE_AWS_REGION)
        users_table = dynamodb.Table(settings.DYNAMODB_TABLE_NAME_USERS)

        try:
            response = users_table.scan(
                FilterExpression="user_type = :user_type",
                ExpressionAttributeValues={":user_type": UserType.STAFF.value},
            )
            users = response.get("Items", [])
            return [UserInDB(**user) for user in users]
        except ClientError as e:
            raise HTTPException(status_code=500, detail=str(e))

    @staticmethod
    async def get_all_normal() -> List[UserInDB]:
        dynamodb = boto3.resource("dynamodb", region_name=settings.PRIVATE_AWS_REGION)
        users_table = dynamodb.Table(settings.DYNAMODB_TABLE_NAME_USERS)

        try:
            response = users_table.scan(
                FilterExpression="user_type = :user_type",
                ExpressionAttributeValues={":user_type": UserType.NORMAL.value},
            )
            users = response.get("Items", [])
            return [UserInDB(**user) for user in users]
        except ClientError as e:
            raise HTTPException(status_code=500, detail=str(e))

    @staticmethod
    async def increment_interaction_counter(user_id: str):
        dynamodb = boto3.resource("dynamodb", region_name=settings.PRIVATE_AWS_REGION)
        users_table = dynamodb.Table(settings.DYNAMODB_TABLE_NAME_USERS)

        try:
            response = users_table.update_item(
                Key={"user_id": user_id},
                UpdateExpression="SET interaction_counter = if_not_exists(interaction_counter, :start) + :inc",
                ExpressionAttributeValues={":inc": 1, ":start": 0},
                ReturnValues="UPDATED_NEW",
            )
            return response["Attributes"]["interaction_counter"]
        except ClientError as e:
            raise HTTPException(status_code=500, detail=str(e))

    @staticmethod
    async def update_preferences(user_id: str, preferences: Preferences):
        dynamodb = boto3.resource("dynamodb", region_name=settings.PRIVATE_AWS_REGION)
        users_table = dynamodb.Table(settings.DYNAMODB_TABLE_NAME_USERS)

        try:
            response = users_table.update_item(
                Key={"user_id": user_id},
                UpdateExpression="SET preferences = :preferences",
                ExpressionAttributeValues={":preferences": preferences.dict()},
                ReturnValues="UPDATED_NEW",
            )
            await UserService.increment_interaction_counter(user_id)
            return response["Attributes"]["preferences"]
        except ClientError as e:
            raise HTTPException(status_code=500, detail=str(e))

    @staticmethod
    async def get_preferences(user_id: str) -> Preferences:
        dynamodb = boto3.resource("dynamodb", region_name=settings.PRIVATE_AWS_REGION)
        users_table = dynamodb.Table(settings.DYNAMODB_TABLE_NAME_USERS)

        try:
            response = users_table.get_item(Key={"user_id": user_id})
            user = response.get("Item")
            if not user or "preferences" not in user:
                raise HTTPException(
                    status_code=404, detail="User or preferences not found"
                )
            await UserService.increment_interaction_counter(user_id)
            return Preferences(**user["preferences"])
        except ClientError as e:
            raise HTTPException(status_code=500, detail=str(e))

    @staticmethod
    async def get_interaction_counter(user_id: str) -> int:
        dynamodb = boto3.resource("dynamodb", region_name=settings.PRIVATE_AWS_REGION)
        users_table = dynamodb.Table(settings.DYNAMODB_TABLE_NAME_USERS)

        try:
            response = users_table.get_item(Key={"user_id": user_id})
            user = response.get("Item")
            if not user or "interaction_counter" not in user:
                raise HTTPException(
                    status_code=404, detail="User or interaction counter not found"
                )
            await UserService.increment_interaction_counter(user_id)
            return user["interaction_counter"]
        except ClientError as e:
            raise HTTPException(status_code=500, detail=str(e))

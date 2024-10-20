import boto3
from botocore.exceptions import ClientError
from fastapi import HTTPException
from core.config import settings
from schemas.user import UserCreate, UserLogin, UserType, StaffType, UserInDB
from typing import List


class UserService:
    @staticmethod
    async def create_user(user: UserCreate):
        cognito_client = boto3.client(
            "cognito-idp",
            region_name=settings.PRIVATE_AWS_REGION,
        )
        dynamodb = boto3.resource("dynamodb", region_name=settings.PRIVATE_AWS_REGION)
        users_table = dynamodb.Table(settings.DYNAMODB_TABLE_NAME)

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
        users_table = dynamodb.Table(settings.DYNAMODB_TABLE_NAME)

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
        users_table = dynamodb.Table(settings.DYNAMODB_TABLE_NAME)

        try:
            # Delete user from Cognito
            cognito_client.admin_delete_user(
                UserPoolId=settings.COGNITO_USER_POOL_ID, Username=user_id
            )

            # Delete user from DynamoDB
            dynamodb_response = users_table.delete_item(Key={"user_id": user_id})

            return {"message": f"User {user_id} deleted successfully"}
        except ClientError as e:
            raise HTTPException(status_code=400, detail=str(e))

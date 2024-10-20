import boto3
from fastapi import Request, Depends, HTTPException
from fastapi.security import APIKeyHeader
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse
from core.config import settings
from schemas.user import User, UserType, StaffType
from botocore.exceptions import ClientError

API_KEY = settings.API_KEY
API_KEY_HEADER = APIKeyHeader(name="API-Key")
USER_ID_HEADER = APIKeyHeader(name="User-ID", auto_error=False)

# Initialize DynamoDB client
dynamodb = boto3.resource("dynamodb", region_name=settings.PRIVATE_AWS_REGION)
users_table = dynamodb.Table(settings.DYNAMODB_TABLE_NAME_USERS)


class AuthMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        if request.url.path in [
            "/docs",
            "/openapi.json",
        ]:  # Skip authentication for Swagger docs
            return await call_next(request)

        api_key = request.headers.get("API-Key")
        if api_key != API_KEY:
            return JSONResponse(
                status_code=403, content={"detail": "Could not validate credentials"}
            )

        user_id = request.headers.get(
            "User-ID", "dhruv@email.com"
        )  # Use default if not provided
        request.state.user_id = user_id  # Store user_id in request state

        return await call_next(request)


async def get_current_user(request: Request) -> User:
    user_id = request.state.user_id
    try:
        response = users_table.get_item(Key={"user_id": user_id})
    except ClientError as e:
        print(f"Error fetching user from DynamoDB: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

    user_data = response.get("Item")
    if not user_data:
        # If user not found, return default user
        return User(
            user_id=user_id,
            email=user_id,
            first_name="Default",
            last_name="User",
            user_type=UserType.NORMAL,
        )

    # Convert DynamoDB data to User object
    user_type = UserType(user_data.get("user_type", UserType.NORMAL))
    staff_type = (
        StaffType(user_data.get("staff_type")) if user_data.get("staff_type") else None
    )

    return User(
        user_id=user_data["user_id"],
        email=user_data["email"],
        first_name=user_data["first_name"],
        last_name=user_data["last_name"],
        user_type=user_type,
        staff_type=staff_type,
    )


# This function can be used as a dependency in your routes
async def get_user_id(
    api_key: str = Depends(API_KEY_HEADER), user_id: str = Depends(USER_ID_HEADER)
):
    if api_key != API_KEY:
        raise HTTPException(status_code=403, detail="Could not validate credentials")
    return user_id or "dhruv@email.com"

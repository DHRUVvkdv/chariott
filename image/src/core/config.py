from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    PROJECT_NAME: str = "CODEFEST-BACKEND"
    API_V1_STR: str = "/api/v1"
    PRIVATE_AWS_ACCESS_KEY_ID: str
    PRIVATE_AWS_SECRET_ACCESS_KEY: str
    PRIVATE_AWS_REGION: str
    S3_BUCKET_NAME: str
    API_KEY: str
    COGNITO_USER_POOL_ID: str
    COGNITO_APP_CLIENT_ID: str
    DYNAMODB_TABLE_NAME: str

    class Config:
        env_file = ".env"


settings = Settings()

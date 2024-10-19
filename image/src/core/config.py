from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    PROJECT_NAME: str = "CODEFEST-BACKEND"
    PRIVATE_AWS_ACCESS_KEY_ID: str
    PRIVATE_AWS_SECRET_ACCESS_KEY: str
    PRIVATE_AWS_REGION: str
    S3_BUCKET_NAME: str
    API_KEY: str

    class Config:
        env_file = ".env"


settings = Settings()

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    PROJECT_NAME: str = "Codefest Application Backend"
    # MONGODB_URL: str
    # DATABASE_NAME: str
    # OPENAI_API_KEY: str

    class Config:
        env_file = ".env"


settings = Settings()

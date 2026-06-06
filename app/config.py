import os
from dotenv import load_dotenv
from pydantic_settings import BaseSettings

load_dotenv()


class Config(BaseSettings):
    app_env: str = os.getenv("APP_ENV", "development")
    log_level: str = os.getenv("LOG_LEVEL", "INFO")
    database_url: str = os.getenv("DATABASE_URL", "sqlite:///./documents.db")
    api_key: str = os.getenv("API_KEY", "")

    @property
    def is_production(self) -> bool:
        return self.app_env == "production"


config = Config()

if not config.api_key:
    raise ValueError("API_KEY is not set in the environment variables")

from dotenv import load_dotenv
from pydantic import Field
from pydantic_settings import BaseSettings

load_dotenv()


class DatabaseConfig(BaseSettings):
    url: str = Field(validation_alias='DATABASE_URL')
    test_url: str = Field(validation_alias='DATABASE_TEST_URL')


class CORSConfig(BaseSettings):
    origins: list[str] = Field(validation_alias='CORS_ORIGINS')
    headers: list[str] = Field(validation_alias='CORS_HEADERS')


class Settings(BaseSettings):
    database: DatabaseConfig = DatabaseConfig()
    cors: CORSConfig = CORSConfig()
    app_port: int = Field(validation_alias='APP_PORT')


def get_settings():
    return Settings()

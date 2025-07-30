from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings
from sqlalchemy import URL


class Settings(BaseSettings):
    POSTGRES_HOST: str = Field(..., env="POSTGRES_HOST")
    POSTGRES_PORT: int = Field(..., env="POSTGRES_PORT")
    POSTGRES_PASSWORD: str = Field(..., env="POSTGRES_PASSWORD")
    POSTGRES_USERNAME: str = Field(..., env="POSTGRES_USERNAME")
    POSTGRES_DB: str = Field(..., env="POSTGRES_DB")

    SERVERS_DIR: str = Field("servers", env="SERVERS_DIR")
    BASE_DIR: str = Field(..., env="BASE_DIR")

    DOCKER_PATH: str = Field(..., env="DOCKER_PATH")

    MINECRAFT_SERVER_MIN_PORT: int = Field(..., env="MINECRAFT_SERVER_MIN_PORT")
    MINECRAFT_SERVER_MAX_PORT: int = Field(..., env="MINECRAFT_SERVER_MAX_PORT")

    def get_db_url(self) -> str:
        return URL.create(
            drivername="postgresql+asyncpg",
            username=self.POSTGRES_USERNAME,
            password=self.POSTGRES_PASSWORD,
            host=self.POSTGRES_HOST,
            port=self.POSTGRES_PORT,
            database=self.POSTGRES_DB,
        ).render_as_string(hide_password=False)

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "allow"


@lru_cache()
def getSettings() -> Settings:
    return Settings()

import logging
from dataclasses import dataclass
from os import getenv
from typing import Literal

from pydantic_settings import BaseSettings
from sqlalchemy import URL
from sqlalchemy.engine import URL

LOG_DEFAULT_FORMAT = (
    "[%(asctime)s.%(msecs)03d] %(module)10s:%(lineno)-3d %(levelname)-7s - %(message)s"
)

WORKER_LOG_DEFAULT_FORMAT = "[%(asctime)s.%(msecs)03d][%(processName)s] %(module)16s:%(lineno)-3d %(levelname)-7s - %(message)s"


class LoggingConfig(BaseSettings):
    log_level: Literal[
        "debug",
        "info",
        "warning",
        "error",
        "critical",
    ] = "info"
    log_format: str = LOG_DEFAULT_FORMAT
    date_format: str = "%Y-%m-%d %H:%M:%S"

    @property
    def log_level_value(self) -> int:
        return logging.getLevelNamesMapping()[self.log_level.upper()]


@dataclass
class DockerConfig:
    server_dir: str = getenv("SERVERS_DIR", "")
    base_dir: str = getenv("BASE_DIR", "minecraft_servers")

    docker_path: str = getenv("DOCKER_PATH", "")

    minecraft_server_min_port: int = int(getenv("MINECRAFT_SERVER_MIN_PORT", 25500))
    minecraft_server_max_port: int = int(getenv("MINECRAFT_SERVER_MAX_PORT", 25600))


@dataclass
class DatabaseConfig:
    """Database connection"""

    name: str = getenv("POSTGRES_DATABASE", "database")
    user: str = getenv("POSTGRES_USER", "user")
    passwd: str = getenv("POSTGRES_PASSWORD", "password")
    port: int = int(getenv("POSTGRES_PORT", 5432))
    host: str = getenv("POSTGRES_HOST", "localhost")

    driver: str = "asyncpg"
    database_system: str = "postgresql"

    def build_connection_str(self) -> str:
        return URL.create(
            drivername=f"{self.database_system}+{self.driver}",
            username=self.user,
            database=self.name,
            password=self.passwd,
            port=self.port,
            host=self.host,
        ).render_as_string(hide_password=False)


@dataclass
class RabbitMQConfig:
    "RabbitMQ configuration"

    host: str = getenv("RABBITMQ_HOST", "localhost")
    port: int = int(getenv("RABBITMQ_PORT", 5672))
    passwd: str | None = getenv("RABBITMQ_PASSWORD")
    username: str | None = getenv("RABBITMQ_USERNAME")

    url: str = f"amqp://{username}:{passwd}@{host}:{port}//"
    log_format: str = WORKER_LOG_DEFAULT_FORMAT


@dataclass
class Configuration:
    db = DatabaseConfig()
    rabbitmq = RabbitMQConfig()
    docker = DockerConfig()
    logging = LoggingConfig()


conf = Configuration()

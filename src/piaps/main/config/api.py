from dataclasses import field
from enum import StrEnum

from piaps.main.config.base import config


class Environment(StrEnum):
    DEV = "development"
    PROD = "production"
    TEST = "testing"


@config
class CORSConfig:
    allow_origins: list[str] = field(default_factory=lambda: ["*"])
    allow_credentials: bool = False
    allow_methods: list[str] = field(default_factory=lambda: ["*"])
    allow_headers: list[str] = field(default_factory=lambda: ["*"])
    max_age: int = 600


@config
class APIConfig:
    host: str = "0.0.0.0"  # noqa: S104
    port: int = 8000
    workers: int = 4
    debug: bool = False
    environment: Environment = Environment.DEV
    cors: CORSConfig = field(default_factory=CORSConfig)

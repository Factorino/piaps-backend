from dataclasses import field

from piaps.main.config.api import APIConfig
from piaps.main.config.base import config
from piaps.main.config.database import DatabaseConfig
from piaps.main.config.jwt import JWTConfig
from piaps.main.config.renderer import RendererConfig


@config
class Config:
    api: APIConfig = field(default_factory=APIConfig)
    database: DatabaseConfig = field(default_factory=DatabaseConfig)
    jwt: JWTConfig = field(default_factory=JWTConfig)
    renderer: RendererConfig = field(default_factory=RendererConfig)

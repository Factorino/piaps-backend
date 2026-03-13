from dishka import BaseScope, Provider, Scope, from_context
from dishka.dependency_source import CompositeDependencySource

from piaps.main.config.api import APIConfig
from piaps.main.config.config import Config
from piaps.main.config.database import DatabaseConfig
from piaps.main.config.jwt import JWTConfig
from piaps.main.config.renderer import RendererConfig


class ConfigProvider(Provider):
    scope: BaseScope | None = Scope.APP

    configs: CompositeDependencySource = (
        from_context(Config)
        + from_context(APIConfig)
        + from_context(DatabaseConfig)
        + from_context(JWTConfig)
        + from_context(RendererConfig)
    )

from dishka import AsyncContainer, Provider, make_async_container
from dishka.integrations.fastapi import FastapiProvider

from piaps.main.config.api import APIConfig
from piaps.main.config.config import Config
from piaps.main.config.database import DatabaseConfig
from piaps.main.config.jwt import JWTConfig
from piaps.main.config.renderer import RendererConfig
from piaps.main.di.providers.auth import AuthProvider
from piaps.main.di.providers.config import ConfigProvider
from piaps.main.di.providers.database import DatabaseProvider
from piaps.main.di.providers.domain import DomainServicesProvider
from piaps.main.di.providers.interactors import InteractorsProvider
from piaps.main.di.providers.readers import ReadersProvider
from piaps.main.di.providers.renderers import ReportRenderersProvider
from piaps.main.di.providers.repositories import RepositoriesProvider


def create_container(config: Config) -> AsyncContainer:
    providers: list[Provider] = [
        FastapiProvider(),
        AuthProvider(),
        ConfigProvider(),
        DatabaseProvider(),
        DomainServicesProvider(),
        InteractorsProvider(),
        ReadersProvider(),
        ReportRenderersProvider(),
        RepositoriesProvider(),
    ]

    context: dict[type, object] = {
        Config: config,
        APIConfig: config.api,
        DatabaseConfig: config.database,
        JWTConfig: config.jwt,
        RendererConfig: config.renderer,
    }

    return make_async_container(*providers, context=context)

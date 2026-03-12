import os
import tomllib
from types import MappingProxyType
from typing import Any, Final

from adaptix import Retort

from piaps.main.config.api import APIConfig
from piaps.main.config.config import Config
from piaps.main.config.database import DatabaseConfig
from piaps.main.config.jwt import JWTConfig
from piaps.main.config.renderer import RendererConfig


DEFAULT_CONFIG_PATH = "./config/configs.toml"
DEFAULT_SECRETS_PATH = "./config/secrets.toml"

_SCOPES: Final[MappingProxyType[type, str]] = MappingProxyType(
    {
        APIConfig: "api",
        DatabaseConfig: "database",
        JWTConfig: "jwt",
        RendererConfig: "renderer",
    }
)


_retort = Retort()


def _read_toml(path: str) -> dict[str, Any]:
    try:
        with open(path, mode="rb") as file:
            return tomllib.load(file)
    except FileNotFoundError:
        return {}
    except tomllib.TOMLDecodeError as e:
        raise RuntimeError(f"Failed to load config: {path}") from e


def _deep_merge(base: dict[str, Any], override: dict[str, Any]) -> dict[str, Any]:
    result: dict[str, Any] = dict(base)
    for key, value in override.items():
        if isinstance(value, dict) and isinstance(result.get(key), dict):
            result[key] = _deep_merge(result[key], value)
        else:
            result[key] = value
    return result


def load_config[CfgT](type: type[CfgT] = Config) -> CfgT:
    configs_path: str = os.getenv("CONFIG_PATH", DEFAULT_CONFIG_PATH)
    secrets_path: str = os.getenv("SECRETS_PATH", DEFAULT_SECRETS_PATH)

    configs_data: dict[str, Any] = _read_toml(configs_path)
    secrets_data: dict[str, Any] = _read_toml(secrets_path)
    data: dict[str, Any] = _deep_merge(configs_data, secrets_data)

    scope: str | None = _SCOPES.get(type)
    if scope:
        data = data.get(scope, {})

    try:
        return _retort.load(data, type)
    except Exception as e:
        raise RuntimeError(f"Failed to load config: {type.__name__}") from e

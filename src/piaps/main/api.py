from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from typing import TYPE_CHECKING

from dishka.integrations.fastapi import setup_dishka
from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware
import uvicorn

from piaps.main.config.config import Config
from piaps.main.config.loader import load_config
from piaps.main.di.container import create_container
from piaps.presentation.api.error_handler import app_error_handler
from piaps.presentation.api.routers.auth import router as auth_router
from piaps.presentation.api.routers.department import router as department_router
from piaps.presentation.api.routers.employee import router as employee_router
from piaps.presentation.api.routers.payroll_item import router as payroll_item_router
from piaps.presentation.api.routers.payroll_sheet import router as payroll_sheet_router
from piaps.presentation.api.routers.position import router as position_router
from piaps.presentation.api.routers.report import router as report_router
from piaps.presentation.api.routers.root import router as root_router
from piaps.presentation.api.routers.user import router as user_router


if TYPE_CHECKING:
    from dishka import AsyncContainer


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    yield
    await app.state.dishka_container.close()


def create_app(config: Config) -> FastAPI:
    app = FastAPI(
        title="PiAPS API",
        version="1.0.0",
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json",
        lifespan=lifespan,
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=config.api.cors.allow_origins,
        allow_credentials=config.api.cors.allow_credentials,
        allow_methods=config.api.cors.allow_methods,
        allow_headers=config.api.cors.allow_headers,
        max_age=config.api.cors.max_age,
    )

    container: AsyncContainer = create_container(config)
    setup_dishka(container, app)

    _include_routers(app)
    app.add_exception_handler(Exception, app_error_handler)

    return app


def _include_routers(app: FastAPI) -> None:
    app.include_router(auth_router)
    app.include_router(department_router)
    app.include_router(employee_router)
    app.include_router(payroll_item_router)
    app.include_router(payroll_sheet_router)
    app.include_router(position_router)
    app.include_router(report_router)
    app.include_router(root_router)
    app.include_router(user_router)


def main() -> None:
    config: Config = load_config(Config)
    app: FastAPI = create_app(config)

    uvicorn.run(
        app,
        host=config.api.host,
        port=config.api.port,
        reload=False,
    )


if __name__ == "__main__":
    main()

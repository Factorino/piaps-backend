from collections.abc import AsyncIterator

from dishka import BaseScope, Provider, Scope, provide
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.ext.asyncio.engine import AsyncEngine

from piaps.application.interfaces.common.transaction_manager import ITransactionManager
from piaps.infrastructure.database.common.transaction_manager import SATransactionManager
from piaps.main.config.database import DatabaseConfig


class DatabaseProvider(Provider):
    scope: BaseScope | None = Scope.APP

    @provide
    async def engine(self, config: DatabaseConfig) -> AsyncIterator[AsyncEngine]:
        engine: AsyncEngine = create_async_engine(config.dsn, echo=False)
        yield engine
        await engine.dispose()

    @provide
    def session_maker(self, engine: AsyncEngine) -> async_sessionmaker[AsyncSession]:
        return async_sessionmaker(bind=engine, expire_on_commit=False, class_=AsyncSession)

    @provide(scope=Scope.REQUEST)
    async def session(
        self, session_maker: async_sessionmaker[AsyncSession]
    ) -> AsyncIterator[AsyncSession]:
        async with session_maker() as session:
            yield session

    @provide(scope=Scope.REQUEST)
    def transaction_manager(self, session: AsyncSession) -> ITransactionManager:
        return SATransactionManager(session)

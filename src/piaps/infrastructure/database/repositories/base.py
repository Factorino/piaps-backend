from abc import ABC, abstractmethod

from sqlalchemy.ext.asyncio import AsyncSession

from piaps.domain.entities.base import Entity
from piaps.infrastructure.database.models.base import BaseORM


class SAAbstractRepository[EntityT: Entity, ORMT: BaseORM](ABC):
    def __init__(self, session: AsyncSession) -> None:
        self._session: AsyncSession = session

    @abstractmethod
    def _to_orm(self, entity: EntityT) -> ORMT:
        raise NotImplementedError

    async def add(self, entity: EntityT) -> None:
        orm_obj: ORMT = self._to_orm(entity)
        self._session.add(orm_obj)

    async def update(self, entity: EntityT) -> None:
        orm_obj: ORMT = self._to_orm(entity)
        await self._session.merge(orm_obj)

    async def delete(self, entity: EntityT) -> None:
        orm_obj: ORMT = self._to_orm(entity)
        merged: ORMT = await self._session.merge(orm_obj)
        await self._session.delete(merged)

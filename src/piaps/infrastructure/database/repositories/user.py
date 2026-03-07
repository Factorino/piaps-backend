from collections.abc import Callable
from uuid import UUID

from adaptix import P
from adaptix.conversion import link
from sqlalchemy.ext.asyncio import AsyncSession

from piaps.application.interfaces.repositories.user import IUserRepository
from piaps.domain.entities.user import User
from piaps.infrastructure.database.common.mapper import get_mapper
from piaps.infrastructure.database.models.user import UserORM
from piaps.infrastructure.database.repositories.base import SAAbstractRepository


class SAUserRepository(IUserRepository, SAAbstractRepository[User, UserORM]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session)

    def _to_orm(self, entity: User) -> UserORM:
        return _to_orm(entity)


_to_orm: Callable[[User], UserORM] = get_mapper(
    User,
    UserORM,
    recipe=[
        link(P[User].username, P[UserORM].username, coercer=lambda u: u.value),
        link(
            P[User].employee_id,
            P[UserORM].employee_id,
            coercer=lambda eid: UUID(str(eid)) if eid is not None else None,
        ),
    ],
)

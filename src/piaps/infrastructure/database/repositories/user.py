from collections.abc import Callable

from adaptix import P
from adaptix.conversion import link

from piaps.domain.entities.user import User
from piaps.infrastructure.database.common.mapper import get_mapper
from piaps.infrastructure.database.models.user import UserORM
from piaps.infrastructure.database.repositories.base import SAAbstractRepository


_to_orm: Callable[[User], UserORM] = get_mapper(
    User,
    UserORM,
    recipe=[
        link(P[User].username, P[UserORM].username, coercer=lambda u: u.value),
    ],
)


class SAUserRepository(SAAbstractRepository[User, UserORM]):
    def _to_orm(self, entity: User) -> UserORM:
        return _to_orm(entity)

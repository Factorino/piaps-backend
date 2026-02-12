from uuid import UUID

from piaps.domain.entities.base import Entity, entity
from piaps.domain.enums.user_role import UserRole


@entity
class User(Entity[UUID]):
    login: str
    password: str
    role: UserRole

    employee_id: UUID | None = None

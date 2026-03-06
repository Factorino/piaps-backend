from typing import NewType
from uuid import UUID

from piaps.domain.entities.base import Entity, entity
from piaps.domain.entities.employee import EmployeeId
from piaps.domain.enums.user_role import UserRole
from piaps.domain.value_objects.username import Username


UserId = NewType("UserId", UUID)


@entity
class User(Entity[UserId]):
    username: Username
    password_hash: bytes
    role: UserRole = UserRole.EMPLOYEE
    employee_id: EmployeeId | None = None

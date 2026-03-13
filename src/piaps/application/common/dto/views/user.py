from typing import Self

from piaps.application.common.dto.base import dto
from piaps.domain.entities.user import EmployeeId, User, UserId
from piaps.domain.enums.user_role import UserRole


@dto
class UserView:
    id: UserId
    username: str
    role: UserRole
    employee_id: EmployeeId | None = None

    @classmethod
    def from_domain(cls, entity: User) -> Self:
        return cls(
            id=entity.id,
            username=entity.username.value,
            role=entity.role,
            employee_id=entity.employee_id,
        )

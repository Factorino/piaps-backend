from typing import Any

from sqlalchemy import UUID, Enum, ForeignKey, LargeBinary, String
from sqlalchemy.orm import Mapped, mapped_column

from piaps.domain.entities.employee import EmployeeId
from piaps.domain.entities.user import UserId
from piaps.domain.enums.user_role import UserRole
from piaps.infrastructure.database.models.base import BaseORM


class UserORM(BaseORM):
    __tablename__: Any = "users"

    id: Mapped[UserId] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
    )

    username: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
        unique=True,
        index=True,
    )

    password_hash: Mapped[bytes] = mapped_column(
        LargeBinary,
        nullable=False,
    )

    role: Mapped[UserRole] = mapped_column(
        Enum(UserRole),
        default=UserRole.EMPLOYEE,
        nullable=False,
    )

    employee_id: Mapped[EmployeeId | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("employees.id"),
        nullable=True,
    )

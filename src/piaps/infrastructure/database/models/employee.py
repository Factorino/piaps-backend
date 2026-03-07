from datetime import date
from typing import Any

from sqlalchemy import UUID, Date, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from piaps.domain.entities.department import DepartmentId
from piaps.domain.entities.employee import EmployeeId
from piaps.domain.entities.position import PositionId
from piaps.infrastructure.database.models.base import BaseORM


class EmployeeORM(BaseORM):
    __tablename__: Any = "employees"

    id: Mapped[EmployeeId] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
    )

    code: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        unique=True,
        index=True,
    )

    full_name: Mapped[str] = mapped_column(
        String(300),
        nullable=False,
        unique=True,
    )

    hire_date: Mapped[date] = mapped_column(
        Date,
        nullable=False,
    )

    department_id: Mapped[DepartmentId] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("departments.id"),
        nullable=False,
        index=True,
    )

    position_id: Mapped[PositionId] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("positions.id"),
        nullable=False,
        index=True,
    )

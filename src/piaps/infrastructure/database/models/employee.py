from datetime import date
from typing import Any
from uuid import UUID

from sqlalchemy import UUID as SAUUID, Date, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from piaps.infrastructure.database.models.base import BaseORM


class EmployeeORM(BaseORM):
    __tablename__: Any = "employees"

    id: Mapped[UUID] = mapped_column(
        SAUUID(as_uuid=True),
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

    position_id: Mapped[UUID] = mapped_column(
        ForeignKey("positions.id"),
        nullable=False,
        index=True,
    )

    department_id: Mapped[UUID] = mapped_column(
        ForeignKey("departments.id"),
        nullable=False,
        index=True,
    )

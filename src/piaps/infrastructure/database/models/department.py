from typing import Any

from sqlalchemy import UUID, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from piaps.domain.entities.department import DepartmentId
from piaps.infrastructure.database.models.base import BaseORM


class DepartmentORM(BaseORM):
    __tablename__: Any = "departments"

    id: Mapped[DepartmentId] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
    )

    code: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        unique=True,
        index=True,
    )

    name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        unique=True,
        index=True,
    )

    description: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

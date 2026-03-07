from typing import Any
from uuid import UUID

from sqlalchemy import UUID as SAUUID, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from piaps.infrastructure.database.models.base import BaseORM


class DepartmentORM(BaseORM):
    __tablename__: Any = "departments"

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

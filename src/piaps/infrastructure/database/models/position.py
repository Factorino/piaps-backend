from decimal import Decimal
from typing import Any

from sqlalchemy import UUID, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from piaps.domain.entities.position import PositionId
from piaps.infrastructure.database.models.base import BaseORM


class PositionORM(BaseORM):
    __tablename__: Any = "positions"

    id: Mapped[PositionId] = mapped_column(
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

    base_salary: Mapped[Decimal] = mapped_column(
        Numeric(15, 2),
        nullable=False,
    )

    description: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

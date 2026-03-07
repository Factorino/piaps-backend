from decimal import Decimal
from typing import Any

from sqlalchemy import UUID, Enum, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column

from piaps.domain.entities.payroll_item import PayrollItemId
from piaps.domain.enums.payroll_calculation_type import PayrollCalculationType
from piaps.domain.enums.payroll_item_type import PayrollItemType
from piaps.infrastructure.database.models.base import BaseORM


class PayrollItemORM(BaseORM):
    __tablename__: Any = "payroll_items"

    id: Mapped[PayrollItemId] = mapped_column(
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

    payroll_type: Mapped[PayrollItemType] = mapped_column(
        Enum(PayrollItemType),
        nullable=False,
        index=True,
    )

    calc_type: Mapped[PayrollCalculationType] = mapped_column(
        Enum(PayrollCalculationType),
        nullable=False,
        index=True,
    )

    value: Mapped[Decimal | None] = mapped_column(
        Numeric(15, 2),
        nullable=True,
    )

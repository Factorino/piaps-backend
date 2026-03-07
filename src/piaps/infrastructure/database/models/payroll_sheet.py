from datetime import date
from typing import Any

from sqlalchemy import UUID, Date, Enum, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from piaps.domain.entities.employee import EmployeeId
from piaps.domain.entities.payroll_sheet import PayrollSheetId
from piaps.domain.enums.payroll_status import PayrollStatus
from piaps.infrastructure.database.models.base import BaseORM
from piaps.infrastructure.database.models.payroll_record import PayrollRecordORM


class PayrollSheetORM(BaseORM):
    __tablename__: Any = "payroll_sheets"

    id: Mapped[PayrollSheetId] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
    )

    employee_id: Mapped[EmployeeId] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("employees.id"),
        nullable=False,
        index=True,
    )

    period: Mapped[date] = mapped_column(
        Date,
        nullable=False,
        index=True,
    )

    status: Mapped[PayrollStatus] = mapped_column(
        Enum(PayrollStatus),
        default=PayrollStatus.DRAFT,
        nullable=False,
    )

    records: Mapped[list[PayrollRecordORM]] = relationship(
        lazy="selectin",
        cascade="all, delete-orphan",
    )

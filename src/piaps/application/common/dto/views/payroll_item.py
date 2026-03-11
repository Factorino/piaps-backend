from decimal import Decimal
from typing import Self

from piaps.application.common.dto.base import dto
from piaps.domain.entities.payroll_item import PayrollItem, PayrollItemId
from piaps.domain.enums.payroll_calculation_type import PayrollCalculationType
from piaps.domain.enums.payroll_item_type import PayrollItemType


@dto
class PayrollItemView:
    id: PayrollItemId
    code: str
    name: str
    payroll_type: PayrollItemType
    calc_type: PayrollCalculationType
    value: Decimal | None = None

    @classmethod
    def from_domain(cls, entity: PayrollItem) -> Self:
        return cls(
            id=entity.id,
            code=entity.code.value,
            name=entity.name.value,
            payroll_type=entity.payroll_type,
            calc_type=entity.calc_type,
            value=entity.value,
        )

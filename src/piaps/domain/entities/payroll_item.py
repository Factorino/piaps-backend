from decimal import Decimal
from typing import NewType
from uuid import UUID

from piaps.domain.entities.base import Entity, entity
from piaps.domain.enums.payroll_calculation_type import PayrollCalculationType
from piaps.domain.enums.payroll_item_type import PayrollItemType
from piaps.domain.errors.base import ValidationError
from piaps.domain.value_objects.code import Code
from piaps.domain.value_objects.name import Name


PayrollItemId = NewType("PayrollItemId", UUID)


@entity
class PayrollItem(Entity[PayrollItemId]):
    code: Code
    name: Name
    payroll_type: PayrollItemType
    calc_type: PayrollCalculationType
    value: Decimal | None = None

    def __post_init__(self) -> None:
        self._validate()

    def _validate(self) -> None:
        if self.calc_type == PayrollCalculationType.PERCENT and self.value is None:
            raise ValidationError(
                f"PayrollItem '{self.name.value}' with calc_type '{self.calc_type}'"
                " must have a value set for percent calculation"
            )

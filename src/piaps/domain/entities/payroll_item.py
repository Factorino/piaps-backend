from typing import NewType
from uuid import UUID

from piaps.domain.entities.base import Entity, entity
from piaps.domain.enums.payroll_calculation_type import PayrollCalculationType
from piaps.domain.enums.payroll_item_type import PayrollItemType
from piaps.domain.value_objects.code import Code
from piaps.domain.value_objects.name import Name


PayrollItemId = NewType("PayrollItemId", UUID)


@entity
class PayrollItem(Entity[PayrollItemId]):
    code: Code
    name: Name
    payroll_type: PayrollItemType
    calc_type: PayrollCalculationType

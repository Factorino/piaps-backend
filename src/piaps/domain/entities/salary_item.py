from decimal import Decimal
from uuid import UUID

from piaps.domain.entities.base import Entity, entity
from piaps.domain.enums.calculation_type import CalculationType
from piaps.domain.enums.salary_item_type import SalaryItemType
from piaps.domain.value_objects.code import Code


@entity
class SalaryItem(Entity[UUID]):
    code: Code
    name: str
    item_type: SalaryItemType
    calc_type: CalculationType
    value: Decimal

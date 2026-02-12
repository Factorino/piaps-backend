from uuid import UUID

from piaps.domain.value_objects.base import ValueObject, value_object
from piaps.domain.value_objects.money import Money


@value_object
class PayrollLineItem(ValueObject):
    salary_item_id: UUID
    amount: Money
    comment: str | None = None

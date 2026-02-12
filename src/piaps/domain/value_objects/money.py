from decimal import Decimal

from piaps.domain.value_objects.base import ValueObject, value_object


@value_object
class Money(ValueObject):
    value: Decimal

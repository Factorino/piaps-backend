from piaps.domain.value_objects.base import ValueObject, value_object


@value_object
class Period(ValueObject):
    year: int
    month: int

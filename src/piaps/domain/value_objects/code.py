from piaps.domain.value_objects.base import ValueObject, value_object


@value_object
class Code(ValueObject):
    value: str

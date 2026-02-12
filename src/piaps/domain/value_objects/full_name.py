from piaps.domain.value_objects.base import ValueObject, value_object


@value_object
class FullName(ValueObject):
    last_name: str
    first_name: str
    middle_name: str | None = None

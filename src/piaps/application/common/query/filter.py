from dataclasses import field
from enum import StrEnum
from typing import Any

from piaps.application.common.dto import dto
from piaps.domain.errors.base import ValidationError


class FilterOperator(StrEnum):
    EQ = "eq"  # value: scalar
    NE = "ne"  # value: scalar
    GT = "gt"  # value: scalar
    GE = "ge"  # value: scalar
    LT = "lt"  # value: scalar
    LE = "le"  # value: scalar
    IN = "in"  # value: list
    NOT_IN = "not_in"  # value: list
    LIKE = "like"  # value: str
    ILIKE = "ilike"  # value: str
    IS_NULL = "is_null"  # value: None
    IS_NOT_NULL = "is_not_null"  # value: None


_ListOperators: list[FilterOperator] = [
    FilterOperator.IN,
    FilterOperator.NOT_IN,
]

_NoValueOperators: list[FilterOperator] = [
    FilterOperator.IS_NULL,
    FilterOperator.IS_NOT_NULL,
]


@dto
class FilterParam[FilterFieldsT: StrEnum]:
    field: FilterFieldsT
    operator: FilterOperator
    value: Any | None = None

    def __post_init__(self) -> None:
        self._validate()

    def _validate(self) -> None:
        if self.operator in _NoValueOperators and self.value is not None:
            raise ValidationError(f"Operator {self.operator} must have value=None")
        if self.operator not in _NoValueOperators and self.value is None:
            raise ValidationError(f"Operator {self.operator} requires a value")
        if self.operator in _ListOperators and not isinstance(self.value, list):
            raise ValidationError(f"Operator {self.operator} requires a list value")


@dto
class Filter[FilterFieldsT: StrEnum]:
    params: list[FilterParam[FilterFieldsT]] = field(default_factory=list)

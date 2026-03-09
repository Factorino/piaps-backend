from dataclasses import field
from enum import StrEnum

from piaps.application.common.dto.base import dto


class OperatorScalar(StrEnum):
    EQ = "eq"
    NE = "ne"
    GT = "gt"
    GE = "ge"
    LT = "lt"
    LE = "le"


class OperatorStr(StrEnum):
    LIKE = "like"
    ILIKE = "ilike"


class OperatorList(StrEnum):
    IN = "in"
    NOT_IN = "not_in"


class OperatorNull(StrEnum):
    IS_NULL = "is_null"
    IS_NOT_NULL = "is_not_null"


@dto
class FilterScalar[FieldT: StrEnum]:
    field: FieldT
    operator: OperatorScalar
    value: int | float | str | bool


@dto
class FilterStr[FieldT: StrEnum]:
    field: FieldT
    operator: OperatorStr
    value: str


@dto
class FilterList[FieldT: StrEnum]:
    field: FieldT
    operator: OperatorList
    value: list[int | float | str | bool]


@dto
class FilterNull[FieldT: StrEnum]:
    field: FieldT
    operator: OperatorNull
    value: None = None


type AnyFilter[FieldT: StrEnum] = (
    FilterScalar[FieldT] | FilterStr[FieldT] | FilterList[FieldT] | FilterNull[FieldT]
)


@dto
class Filter[FieldT: StrEnum]:
    params: list[AnyFilter[FieldT]] = field(default_factory=list)

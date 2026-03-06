from dataclasses import field
from enum import StrEnum

from piaps.application.common.dto.base import dto


class SortDirection(StrEnum):
    ASC = "asc"
    DESC = "desc"


@dto
class SortParam[FieldT: StrEnum]:
    field: FieldT
    direction: SortDirection = SortDirection.ASC


@dto
class Sort[FieldT: StrEnum]:
    params: list[SortParam[FieldT]] = field(default_factory=list)

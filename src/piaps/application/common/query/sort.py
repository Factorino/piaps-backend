from dataclasses import field
from enum import StrEnum

from piaps.application.common.dto import dto


class SortDirection(StrEnum):
    ASC = "asc"
    DESC = "desc"


@dto
class SortParam[SortFieldsT: StrEnum]:
    field: SortFieldsT
    direction: SortDirection = SortDirection.ASC


@dto
class Sort[SortFieldsT: StrEnum]:
    params: list[SortParam[SortFieldsT]] = field(default_factory=list)

from typing import ClassVar
import uuid

from piaps.domain.entities.department import Department
from piaps.domain.entities.employee import Employee
from piaps.domain.entities.position import Position
from piaps.domain.entities.salary_item import SalaryItem
from piaps.domain.errors.base import DomainError
from piaps.domain.value_objects.code import Code


class CodeGenerator:
    _UUID_LENGTH: ClassVar[int] = 12
    _PREFIXES: ClassVar[dict[type, str]] = {
        Department: "DEP",
        Employee: "EMPL",
        Position: "POS",
        SalaryItem: "SAL",
    }

    def generate(self, entity: object) -> Code:
        entity_type = type(entity)
        prefix: str | None = self._PREFIXES.get(entity_type)

        if prefix is None:
            raise DomainError

        return self._generate_code(prefix)

    def _generate_code(self, prefix: str) -> Code:
        short_uid: str = uuid.uuid4().hex[: self._UUID_LENGTH]
        return Code(value=f"{prefix}_{short_uid}")

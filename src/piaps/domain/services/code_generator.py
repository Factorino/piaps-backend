from types import MappingProxyType
from typing import Final
import uuid

from piaps.domain.entities.base import Entity
from piaps.domain.entities.department import Department
from piaps.domain.entities.employee import Employee
from piaps.domain.entities.payroll_item import PayrollItem
from piaps.domain.entities.position import Position
from piaps.domain.value_objects.code import Code


class CodeGenerator:
    _PREFIXES: Final[MappingProxyType[type, str]] = MappingProxyType(
        {
            Department: "DEP",
            Employee: "EMPL",
            PayrollItem: "PRL",
            Position: "POS",
        }
    )

    def generate(self, entity_type: type[Entity]) -> Code:
        prefix: str | None = self._PREFIXES.get(entity_type)
        if prefix is None:
            raise ValueError(f"No code prefix registered for entity type '{entity_type.__name__}'")

        uid: str = uuid.uuid4().hex[: Code.UID_LENGTH]
        return Code(prefix=prefix, uid=uid)

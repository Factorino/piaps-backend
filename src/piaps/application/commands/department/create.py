from typing import TYPE_CHECKING
from uuid import uuid4

from piaps.application.common.dto import base
from piaps.application.interfaces.interactor import IInteractor
from piaps.application.interfaces.readers.department import IDepartmentReader
from piaps.application.interfaces.repositories.department import IDepartmentRepository
from piaps.application.interfaces.transaction_manager import TransactionManager
from piaps.domain.entities.department import Department
from piaps.domain.errors.base import AlreadyExistsError
from piaps.domain.services.code_generator import CodeGenerator


if TYPE_CHECKING:
    from piaps.domain.value_objects.code import Code


@base
class CreateDepartmentRequest:
    name: str
    description: str | None = None


@base
class CreateDepartmentResponse:
    department: Department


class CreateDepartment(IInteractor[CreateDepartmentRequest, CreateDepartmentResponse]):
    def __init__(
        self,
        department_repository: IDepartmentRepository,
        department_reader: IDepartmentReader,
        code_generator: CodeGenerator,
        uow: TransactionManager,
    ) -> None:
        self._repository: IDepartmentRepository = department_repository
        self._reader: IDepartmentReader = department_reader
        self._code_generator: CodeGenerator = code_generator
        self._uow: TransactionManager = uow

    async def execute(self, request: CreateDepartmentRequest) -> CreateDepartmentResponse:
        code: Code = self._code_generator.generate(Department)

        existing: Department | None = await self._reader.find_by_code(code)
        if existing is not None:
            raise AlreadyExistsError

        department = Department(
            id=uuid4(),
            code=code,
            name=request.name,
            description=request.description,
        )

        saved: Department = await self._repository.add(department)
        await self._uow.commit()

        return CreateDepartmentResponse(department=saved)

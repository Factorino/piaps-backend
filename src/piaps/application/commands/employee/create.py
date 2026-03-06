from datetime import date
from typing import TYPE_CHECKING
from uuid import UUID, uuid4

from piaps.application.common.dto import dto
from piaps.application.interfaces.interactor import IInteractor
from piaps.application.interfaces.readers.department import IDepartmentReader
from piaps.application.interfaces.readers.employee import IEmployeeReader
from piaps.application.interfaces.readers.position import IPositionReader
from piaps.application.interfaces.repositories.employee import IEmployeeRepository
from piaps.application.interfaces.transaction_manager import TransactionManager
from piaps.domain.entities.employee import Employee
from piaps.domain.errors.base import AlreadyExistsError
from piaps.domain.services.code_generator import CodeGenerator


if TYPE_CHECKING:
    from piaps.domain.value_objects.code import Code


@dto
class CreateEmployeeRequest:
    last_name: str
    first_name: str
    middle_name: str | None
    hire_date: date
    position_id: UUID
    department_id: UUID


@dto
class CreateEmployeeResponse:
    employee: Employee


class CreateEmployee(IInteractor[CreateEmployeeRequest, CreateEmployeeResponse]):
    def __init__(
        self,
        repository: IEmployeeRepository,
        employee_reader: IEmployeeReader,
        position_reader: IPositionReader,
        department_reader: IDepartmentReader,
        code_generator: CodeGenerator,
        uow: TransactionManager,    
    ) -> None:
        self._repository: IEmployeeRepository = repository
        self._employee_reader: IEmployeeReader = employee_reader
        self._position_reader: IPositionReader = position_reader
        self._department_reader: IDepartmentReader = department_reader
        self._code_generator: CodeGenerator = code_generator
        self._uow: TransactionManager = uow

    async def execute(self, request: CreateEmployeeRequest) -> CreateEmployeeResponse:
        code: Code = self._code_generator.generate(Employee)

        existing: Employee | None = await self._reader.find_by_code(code)
        if existing is not None:
            raise AlreadyExistsError

        employee = Employee(
            id=uuid4(),
            code=code,
            name=request.name,
            description=request.description,
        )

        saved: Employee = await self._repository.add(employee)
        await self._uow.commit()

        return CreateEmployeeResponse(employee=saved)

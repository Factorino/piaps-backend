from datetime import date
from typing import Final
from uuid import uuid4

from piaps.application.common.dto.base import dto
from piaps.application.common.dto.employee import EmployeeDTO
from piaps.application.errors.auth import AccessDeniedError
from piaps.application.errors.base import OperationFailedError
from piaps.application.interfaces.auth.identity_provider import IIdentityProvider
from piaps.application.interfaces.common.interactor import Interactor
from piaps.application.interfaces.common.transaction_manager import ITransactionManager
from piaps.application.interfaces.readers.employee import IEmployeeReader
from piaps.application.interfaces.repositories.employee import IEmployeeRepository
from piaps.domain.entities.department import DepartmentId
from piaps.domain.entities.employee import Employee, EmployeeId
from piaps.domain.entities.position import PositionId
from piaps.domain.entities.user import User
from piaps.domain.enums.user_role import UserRole
from piaps.domain.services.code_generator import CodeGenerator
from piaps.domain.value_objects.code import Code
from piaps.domain.value_objects.full_name import FullName


@dto
class CreateEmployeeRequest:
    last_name: str
    first_name: str
    middle_name: str | None = None
    hire_date: date
    department_id: DepartmentId
    position_id: PositionId


@dto
class CreateEmployeeResponse:
    employee: EmployeeDTO


class CreateEmployee(Interactor[CreateEmployeeRequest, CreateEmployeeResponse]):
    _MAX_CODE_GEN_ATTEMPTS: Final[int] = 5

    def __init__(
        self,
        employee_repository: IEmployeeRepository,
        employee_reader: IEmployeeReader,
        code_generator: CodeGenerator,
        transaction_manager: ITransactionManager,
        identity_provider: IIdentityProvider,
    ) -> None:
        self._employee_repository: IEmployeeRepository = employee_repository
        self._employee_reader: IEmployeeReader = employee_reader
        self._code_generator: CodeGenerator = code_generator
        self._uow: ITransactionManager = transaction_manager
        self._idp: IIdentityProvider = identity_provider

    async def execute(self, request: CreateEmployeeRequest) -> CreateEmployeeResponse:
        current_user: User = await self._idp.get_user()
        self._check_access(current_user)

        code: Code = await self._generate_unique_code()
        full_name = FullName(
            last_name=request.last_name,
            first_name=request.first_name,
            middle_name=request.middle_name,
        )

        employee = Employee(
            id=EmployeeId(uuid4()),
            code=code,
            full_name=full_name,
            hire_date=request.hire_date,
            department_id=request.department_id,
            position_id=request.position_id,
        )

        await self._employee_repository.add(employee)
        await self._uow.commit()

        return CreateEmployeeResponse(employee=EmployeeDTO.from_domain(employee))

    async def _generate_unique_code(self) -> Code:
        for _ in range(self._MAX_CODE_GEN_ATTEMPTS):
            code: Code = self._code_generator.generate(Employee)

            existing: Employee | None = await self._employee_reader.find_by_code(code)
            if existing is None:
                return code

        raise OperationFailedError(
            f"Failed to generate unique code for employee "
            f"after {self._MAX_CODE_GEN_ATTEMPTS} attempts"
        )

    def _check_access(self, current_user: User) -> None:
        if current_user.role < UserRole.ADMINISTRATOR:
            raise AccessDeniedError("You don't have permission to create employees")

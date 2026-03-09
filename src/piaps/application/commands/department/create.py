from typing import Final
from uuid import uuid4

from piaps.application.common.dto.base import dto
from piaps.application.common.dto.department import DepartmentDTO
from piaps.application.errors.auth import AccessDeniedError
from piaps.application.errors.base import OperationFailedError
from piaps.application.interfaces.auth.identity_provider import IIdentityProvider
from piaps.application.interfaces.common.interactor import Interactor
from piaps.application.interfaces.common.transaction_manager import ITransactionManager
from piaps.application.interfaces.readers.department import IDepartmentReader
from piaps.application.interfaces.repositories.department import IDepartmentRepository
from piaps.domain.entities.department import Department, DepartmentId
from piaps.domain.entities.user import User
from piaps.domain.enums.user_role import UserRole
from piaps.domain.errors.base import AlreadyExistsError
from piaps.domain.services.code_generator import CodeGenerator
from piaps.domain.value_objects.code import Code
from piaps.domain.value_objects.name import Name


@dto
class CreateDepartmentRequest:
    name: str
    description: str | None = None


@dto
class CreateDepartmentResponse:
    department: DepartmentDTO


class CreateDepartment(Interactor[CreateDepartmentRequest, CreateDepartmentResponse]):
    _MAX_CODE_GEN_ATTEMPTS: Final[int] = 5

    def __init__(
        self,
        department_repository: IDepartmentRepository,
        department_reader: IDepartmentReader,
        code_generator: CodeGenerator,
        transaction_manager: ITransactionManager,
        identity_provider: IIdentityProvider,
    ) -> None:
        self._department_repository: IDepartmentRepository = department_repository
        self._department_reader: IDepartmentReader = department_reader
        self._code_generator: CodeGenerator = code_generator
        self._uow: ITransactionManager = transaction_manager
        self._idp: IIdentityProvider = identity_provider

    async def execute(self, request: CreateDepartmentRequest) -> CreateDepartmentResponse:
        current_user: User = await self._idp.get_user()
        self._check_access(current_user)

        id_: DepartmentId = DepartmentId(uuid4())
        code: Code = await self._generate_unique_code()
        name = Name(value=request.name)
        description: str | None = request.description

        department = Department(
            id=id_,
            code=code,
            name=name,
            description=description,
        )

        await self._check_unique(department)
        await self._department_repository.add(department)
        await self._uow.commit()

        return CreateDepartmentResponse(department=DepartmentDTO.from_domain(department))

    async def _generate_unique_code(self) -> Code:
        for _ in range(self._MAX_CODE_GEN_ATTEMPTS):
            code: Code = self._code_generator.generate(Department)

            existing: Department | None = await self._department_reader.find_by_code(code)
            if existing is None:
                return code

        raise OperationFailedError(
            f"Failed to generate unique code for department "
            f"after {self._MAX_CODE_GEN_ATTEMPTS} attempts"
        )

    async def _check_unique(self, department: Department) -> None:
        existing: Department | None = await self._department_reader.find_by_name(department.name)
        if existing is not None and existing.id != department.id:
            raise AlreadyExistsError(
                f"Department with name '{department.name.value}' already exists"
            )

    def _check_access(self, current_user: User) -> None:
        if current_user.role < UserRole.ADMINISTRATOR:
            raise AccessDeniedError("You don't have permission to create departments")

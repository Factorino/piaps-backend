from typing import TYPE_CHECKING, Final
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
from piaps.domain.enums.user_role import UserRole
from piaps.domain.errors.base import AlreadyExistsError
from piaps.domain.services.code_generator import CodeGenerator
from piaps.domain.value_objects.code import Code
from piaps.domain.value_objects.name import Name


if TYPE_CHECKING:
    from piaps.domain.entities.user import User


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
        await self._check_access()

        code: Code = await self._generate_unique_code()

        existing: Department | None = await self._department_reader.find_by_code(code)
        if existing is not None:
            raise AlreadyExistsError(f"Department with code '{code.value}' already exists")

        department = Department(
            id=DepartmentId(uuid4()),
            code=code,
            name=Name(value=request.name),
            description=request.description,
        )

        await self._department_repository.add(department)
        await self._uow.commit()

        return CreateDepartmentResponse(department=DepartmentDTO.from_domain(department))

    async def _check_access(self) -> None:
        user: User = await self._idp.get_user()
        if user.role < UserRole.ADMINISTRATOR:
            raise AccessDeniedError("Only administrators can create departments")

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

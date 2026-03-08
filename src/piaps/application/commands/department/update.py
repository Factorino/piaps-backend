from typing import TYPE_CHECKING

from piaps.application.common.dto.base import dto
from piaps.application.common.dto.department import DepartmentDTO
from piaps.application.common.not_set import NOTSET, NotSet, is_set
from piaps.application.errors.auth import AccessDeniedError
from piaps.application.interfaces.auth.identity_provider import IIdentityProvider
from piaps.application.interfaces.common.interactor import Interactor
from piaps.application.interfaces.common.transaction_manager import ITransactionManager
from piaps.application.interfaces.readers.department import IDepartmentReader
from piaps.application.interfaces.repositories.department import IDepartmentRepository
from piaps.domain.entities.department import Department, DepartmentId
from piaps.domain.enums.user_role import UserRole
from piaps.domain.errors.base import NotFoundError
from piaps.domain.value_objects.name import Name


if TYPE_CHECKING:
    from piaps.domain.entities.user import User


@dto
class UpdateDepartmentRequest:
    id: DepartmentId
    name: str | NotSet = NOTSET
    description: str | None | NotSet = NOTSET


@dto
class UpdateDepartmentResponse:
    department: DepartmentDTO


class UpdateDepartment(Interactor[UpdateDepartmentRequest, UpdateDepartmentResponse]):
    def __init__(
        self,
        department_repository: IDepartmentRepository,
        department_reader: IDepartmentReader,
        transaction_manager: ITransactionManager,
        identity_provider: IIdentityProvider,
    ) -> None:
        self._department_repository: IDepartmentRepository = department_repository
        self._department_reader: IDepartmentReader = department_reader
        self._uow: ITransactionManager = transaction_manager
        self._idp: IIdentityProvider = identity_provider

    async def execute(self, request: UpdateDepartmentRequest) -> UpdateDepartmentResponse:
        await self._check_access()

        department: Department | None = await self._department_reader.find_by_id(request.id)
        if department is None:
            raise NotFoundError(f"Department with id '{request.id}' not found")

        if is_set(request.name):
            department.name = Name(value=request.name)
        if is_set(request.description):
            department.description = request.description

        await self._department_repository.update(department)
        await self._uow.commit()

        return UpdateDepartmentResponse(department=DepartmentDTO.from_domain(department))

    async def _check_access(self) -> None:
        user: User = await self._idp.get_user()
        if user.role < UserRole.ADMINISTRATOR:
            raise AccessDeniedError("Only administrators can update departments")

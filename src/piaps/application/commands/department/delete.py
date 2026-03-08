from typing import TYPE_CHECKING

from piaps.application.common.dto.base import dto
from piaps.application.errors.auth import AccessDeniedError
from piaps.application.interfaces.auth.identity_provider import IIdentityProvider
from piaps.application.interfaces.common.interactor import Interactor
from piaps.application.interfaces.common.transaction_manager import ITransactionManager
from piaps.application.interfaces.readers.department import IDepartmentReader
from piaps.application.interfaces.repositories.department import IDepartmentRepository
from piaps.domain.entities.department import DepartmentId
from piaps.domain.enums.user_role import UserRole
from piaps.domain.errors.base import NotFoundError


if TYPE_CHECKING:
    from piaps.domain.entities.department import Department
    from piaps.domain.entities.user import User


@dto
class DeleteDepartmentRequest:
    id: DepartmentId


class DeleteDepartment(Interactor[DeleteDepartmentRequest, None]):
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

    async def execute(self, request: DeleteDepartmentRequest) -> None:
        await self._check_access()

        department: Department | None = await self._department_reader.find_by_id(request.id)
        if department is None:
            raise NotFoundError(f"Department with id '{request.id}' not found")

        await self._department_repository.delete(department)
        await self._uow.commit()

    async def _check_access(self) -> None:
        user: User = await self._idp.get_user()
        if user.role < UserRole.ADMINISTRATOR:
            raise AccessDeniedError("Only administrators can delete departments")

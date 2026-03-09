from typing import TYPE_CHECKING

from piaps.application.common.dto.base import dto
from piaps.application.errors.auth import AccessDeniedError
from piaps.application.interfaces.auth.identity_provider import IIdentityProvider
from piaps.application.interfaces.common.interactor import Interactor
from piaps.application.interfaces.common.transaction_manager import ITransactionManager
from piaps.application.interfaces.readers.department import IDepartmentReader
from piaps.application.interfaces.repositories.department import IDepartmentRepository
from piaps.domain.entities.department import DepartmentId
from piaps.domain.entities.user import User
from piaps.domain.enums.user_role import UserRole
from piaps.domain.errors.base import NotFoundError


if TYPE_CHECKING:
    from piaps.domain.entities.department import Department


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
        current_user: User = await self._idp.get_user()
        self._check_access(current_user)

        department: Department | None = await self._department_reader.find_by_id(request.id)
        if department is None:
            raise NotFoundError(f"Department with id '{request.id}' not found")

        await self._department_repository.delete(department)
        await self._uow.commit()

    def _check_access(self, current_user: User) -> None:
        if current_user.role < UserRole.ADMINISTRATOR:
            raise AccessDeniedError("You don't have permission to delete departments")

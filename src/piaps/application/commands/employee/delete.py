from typing import TYPE_CHECKING

from piaps.application.common.dto.base import dto
from piaps.application.errors.auth import AccessDeniedError
from piaps.application.interfaces.auth.identity_provider import IIdentityProvider
from piaps.application.interfaces.common.interactor import Interactor
from piaps.application.interfaces.common.transaction_manager import ITransactionManager
from piaps.application.interfaces.readers.employee import IEmployeeReader
from piaps.application.interfaces.repositories.employee import IEmployeeRepository
from piaps.domain.entities.employee import EmployeeId
from piaps.domain.entities.user import User
from piaps.domain.enums.user_role import UserRole
from piaps.domain.errors.base import NotFoundError


if TYPE_CHECKING:
    from piaps.domain.entities.employee import Employee


@dto
class DeleteEmployeeRequest:
    id: EmployeeId


class DeleteEmployee(Interactor[DeleteEmployeeRequest, None]):
    def __init__(
        self,
        employee_repository: IEmployeeRepository,
        employee_reader: IEmployeeReader,
        transaction_manager: ITransactionManager,
        identity_provider: IIdentityProvider,
    ) -> None:
        self._employee_repository: IEmployeeRepository = employee_repository
        self._employee_reader: IEmployeeReader = employee_reader
        self._uow: ITransactionManager = transaction_manager
        self._idp: IIdentityProvider = identity_provider

    async def execute(self, request: DeleteEmployeeRequest) -> None:
        current_user: User = await self._idp.get_user()
        self._check_access(current_user)

        employee: Employee | None = await self._employee_reader.find_by_id(request.id)
        if employee is None:
            raise NotFoundError(f"Employee with id '{request.id}' not found")

        await self._employee_repository.delete(employee)
        await self._uow.commit()

    def _check_access(self, current_user: User) -> None:
        if current_user.role < UserRole.ADMINISTRATOR:
            raise AccessDeniedError("You don't have permission to delete employees")

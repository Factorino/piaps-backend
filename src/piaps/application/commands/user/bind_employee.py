from typing import TYPE_CHECKING

from piaps.application.common.dto.base import dto
from piaps.application.common.dto.views.user import UserView
from piaps.application.errors.auth import AccessDeniedError
from piaps.application.interfaces.auth.identity_provider import IIdentityProvider
from piaps.application.interfaces.common.interactor import Interactor
from piaps.application.interfaces.common.transaction_manager import ITransactionManager
from piaps.application.interfaces.readers.employee import IEmployeeReader
from piaps.application.interfaces.readers.user import IUserReader
from piaps.application.interfaces.repositories.user import IUserRepository
from piaps.domain.entities.user import User, UserId
from piaps.domain.enums.user_role import UserRole
from piaps.domain.errors.base import AlreadyExistsError, NotFoundError
from piaps.domain.value_objects.code import Code


if TYPE_CHECKING:
    from piaps.domain.entities.employee import Employee


@dto
class BindEmployeeBody:
    employee_code: str | None  # None => unbind


@dto
class BindEmployeeRequest:
    id: UserId
    body: BindEmployeeBody


@dto
class BindEmployeeResponse:
    user: UserView


class BindEmployee(Interactor[BindEmployeeRequest, BindEmployeeResponse]):
    def __init__(
        self,
        user_repository: IUserRepository,
        user_reader: IUserReader,
        employee_reader: IEmployeeReader,
        transaction_manager: ITransactionManager,
        identity_provider: IIdentityProvider,
    ) -> None:
        self._user_repository: IUserRepository = user_repository
        self._user_reader: IUserReader = user_reader
        self._employee_reader: IEmployeeReader = employee_reader
        self._uow: ITransactionManager = transaction_manager
        self._idp: IIdentityProvider = identity_provider

    async def execute(self, request: BindEmployeeRequest) -> BindEmployeeResponse:
        current_user: User = await self._idp.get_user()
        self._check_access(current_user, request.id)

        user: User | None = await self._user_reader.find_by_id(request.id)
        if user is None:
            raise NotFoundError(f"User with id '{request.id}' not found")

        if request.body.employee_code is None:
            user.employee_id = None
        else:
            code: Code = Code.from_str(request.body.employee_code)
            employee: Employee | None = await self._employee_reader.find_by_code(code)
            if employee is None:
                raise NotFoundError(f"Employee with code '{code.value}' not found")

            user.employee_id = employee.id
            await self._check_unique(user)

        await self._user_repository.update(user)
        await self._uow.commit()

        return BindEmployeeResponse(user=UserView.from_domain(user))

    async def _check_unique(self, user: User) -> None:
        if user.employee_id is None:
            return

        existing: User | None = await self._user_reader.find_by_employee(user.employee_id)
        if existing is not None and existing.id != user.id:
            raise AlreadyExistsError(f"User with employee_id '{user.employee_id}' already exists")

    def _check_access(self, current_user: User, target_user_id: UserId) -> None:
        if current_user.role < UserRole.ADMINISTRATOR and current_user.id != target_user_id:
            raise AccessDeniedError(
                "You don't have permission to bind or unbind an employee to another user"
            )

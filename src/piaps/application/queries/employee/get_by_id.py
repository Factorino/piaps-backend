from piaps.application.common.dto.base import dto
from piaps.application.common.dto.views.employee import EmployeeView
from piaps.application.errors.auth import AccessDeniedError
from piaps.application.interfaces.auth.identity_provider import IIdentityProvider
from piaps.application.interfaces.common.interactor import Interactor
from piaps.application.interfaces.readers.employee import IEmployeeReader
from piaps.domain.entities.employee import Employee, EmployeeId
from piaps.domain.entities.user import User
from piaps.domain.enums.user_role import UserRole
from piaps.domain.errors.base import NotFoundError


@dto
class GetEmployeeByIdRequest:
    id: EmployeeId


@dto
class GetEmployeeByIdResponse:
    user: EmployeeView


class GetEmployeeById(Interactor[GetEmployeeByIdRequest, GetEmployeeByIdResponse]):
    def __init__(
        self,
        employee_reader: IEmployeeReader,
        identity_provider: IIdentityProvider,
    ) -> None:
        self._employee_reader: IEmployeeReader = employee_reader
        self._idp: IIdentityProvider = identity_provider

    async def execute(self, request: GetEmployeeByIdRequest) -> GetEmployeeByIdResponse:
        current_user: User = await self._idp.get_user()
        self._check_access(current_user)

        employee: Employee | None = await self._employee_reader.find_by_id(request.id)
        if employee is None:
            raise NotFoundError(f"Employee with id '{request.id}' not found")

        return GetEmployeeByIdResponse(user=EmployeeView.from_domain(employee))

    def _check_access(self, current_user: User) -> None:
        if current_user.role < UserRole.ACCOUNTANT:
            raise AccessDeniedError("You don't have permission to read employees")

from piaps.application.common.dto.base import dto
from piaps.application.common.dto.views.department import DepartmentView
from piaps.application.errors.auth import AccessDeniedError
from piaps.application.interfaces.auth.identity_provider import IIdentityProvider
from piaps.application.interfaces.common.interactor import Interactor
from piaps.application.interfaces.readers.department import IDepartmentReader
from piaps.domain.entities.department import Department, DepartmentId
from piaps.domain.entities.user import User
from piaps.domain.enums.user_role import UserRole
from piaps.domain.errors.base import NotFoundError


@dto
class GetDepartmentByIdRequest:
    id: DepartmentId


@dto
class GetDepartmentByIdResponse:
    user: DepartmentView


class GetDepartmentById(Interactor[GetDepartmentByIdRequest, GetDepartmentByIdResponse]):
    def __init__(
        self,
        department_reader: IDepartmentReader,
        identity_provider: IIdentityProvider,
    ) -> None:
        self._department_reader: IDepartmentReader = department_reader
        self._idp: IIdentityProvider = identity_provider

    async def execute(self, request: GetDepartmentByIdRequest) -> GetDepartmentByIdResponse:
        current_user: User = await self._idp.get_user()
        self._check_access(current_user)

        department: Department | None = await self._department_reader.find_by_id(request.id)
        if department is None:
            raise NotFoundError(f"Department with id '{request.id}' not found")

        return GetDepartmentByIdResponse(user=DepartmentView.from_domain(department))

    def _check_access(self, current_user: User) -> None:
        if current_user.role < UserRole.ACCOUNTANT:
            raise AccessDeniedError("You don't have permission to read departments")

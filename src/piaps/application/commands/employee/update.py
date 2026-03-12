from piaps.application.common.dto.base import dto
from piaps.application.common.dto.views.employee import EmployeeView
from piaps.application.common.not_set import NOTSET, NotSet, is_set
from piaps.application.errors.auth import AccessDeniedError
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
from piaps.domain.errors.base import NotFoundError
from piaps.domain.value_objects.full_name import FullName


@dto
class UpdateEmployeeBody:
    last_name: str | NotSet = NOTSET
    first_name: str | NotSet = NOTSET
    middle_name: str | None | NotSet = NOTSET
    department_id: DepartmentId | NotSet = NOTSET
    position_id: PositionId | NotSet = NOTSET


@dto
class UpdateEmployeeRequest:
    id: EmployeeId
    body: UpdateEmployeeBody


@dto
class UpdateEmployeeResponse:
    employee: EmployeeView


class UpdateEmployee(Interactor[UpdateEmployeeRequest, UpdateEmployeeResponse]):
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

    async def execute(self, request: UpdateEmployeeRequest) -> UpdateEmployeeResponse:
        current_user: User = await self._idp.get_user()
        self._check_access(current_user)

        employee: Employee | None = await self._employee_reader.find_by_id(request.id)
        if employee is None:
            raise NotFoundError(f"Employee with id '{request.id}' not found")

        employee.full_name = self._build_full_name(employee, request)
        if is_set(request.body.department_id):
            employee.department_id = request.body.department_id
        if is_set(request.body.position_id):
            employee.position_id = request.body.position_id

        await self._employee_repository.update(employee)
        await self._uow.commit()

        return UpdateEmployeeResponse(employee=EmployeeView.from_domain(employee))

    def _build_full_name(self, entity: Employee, request: UpdateEmployeeRequest) -> FullName:
        last_name: str = entity.full_name.last_name
        if is_set(request.body.last_name):
            last_name = request.body.last_name

        first_name: str = entity.full_name.first_name
        if is_set(request.body.first_name):
            first_name = request.body.first_name

        middle_name: str | None = entity.full_name.middle_name
        if is_set(request.body.middle_name):
            middle_name = request.body.middle_name

        return FullName(last_name=last_name, first_name=first_name, middle_name=middle_name)

    def _check_access(self, current_user: User) -> None:
        if current_user.role < UserRole.ADMINISTRATOR:
            raise AccessDeniedError("You don't have permission to update employees")

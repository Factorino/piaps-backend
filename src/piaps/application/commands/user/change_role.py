from piaps.application.common.dto.base import dto
from piaps.application.common.dto.views.user import UserView
from piaps.application.errors.auth import AccessDeniedError
from piaps.application.interfaces.auth.identity_provider import IIdentityProvider
from piaps.application.interfaces.common.interactor import Interactor
from piaps.application.interfaces.common.transaction_manager import ITransactionManager
from piaps.application.interfaces.readers.user import IUserReader
from piaps.application.interfaces.repositories.user import IUserRepository
from piaps.domain.entities.user import User, UserId
from piaps.domain.enums.user_role import UserRole
from piaps.domain.errors.base import NotFoundError


@dto
class ChangeUserRoleRequest:
    id: UserId
    role: UserRole


@dto
class ChangeUserRoleResponse:
    user: UserView


class ChangeUserRole(Interactor[ChangeUserRoleRequest, ChangeUserRoleResponse]):
    def __init__(
        self,
        user_repository: IUserRepository,
        user_reader: IUserReader,
        transaction_manager: ITransactionManager,
        identity_provider: IIdentityProvider,
    ) -> None:
        self._user_repository: IUserRepository = user_repository
        self._user_reader: IUserReader = user_reader
        self._uow: ITransactionManager = transaction_manager
        self._idp: IIdentityProvider = identity_provider

    async def execute(self, request: ChangeUserRoleRequest) -> ChangeUserRoleResponse:
        current_user: User = await self._idp.get_user()
        self._check_access(current_user, request.id)

        user: User | None = await self._user_reader.find_by_id(request.id)
        if user is None:
            raise NotFoundError(f"User with id '{request.id}' not found")

        user.role = request.role

        await self._user_repository.update(user)
        await self._uow.commit()

        return ChangeUserRoleResponse(user=UserView.from_domain(user))

    def _check_access(self, current_user: User, target_user_id: UserId) -> None:
        if current_user.id == target_user_id:
            raise AccessDeniedError("You cannot change your own role")

        if current_user.role < UserRole.ADMINISTRATOR:
            raise AccessDeniedError("You don't have permission to change another user's role")

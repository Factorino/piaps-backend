from piaps.application.common.dto.base import dto
from piaps.application.common.dto.views.user import UserView
from piaps.application.errors.auth import AccessDeniedError
from piaps.application.interfaces.auth.identity_provider import IIdentityProvider
from piaps.application.interfaces.auth.password_hasher import IPasswordHasher
from piaps.application.interfaces.common.interactor import Interactor
from piaps.application.interfaces.common.transaction_manager import ITransactionManager
from piaps.application.interfaces.readers.user import IUserReader
from piaps.application.interfaces.repositories.user import IUserRepository
from piaps.domain.entities.user import User, UserId
from piaps.domain.enums.user_role import UserRole
from piaps.domain.errors.base import NotFoundError, ValidationError
from piaps.domain.value_objects.password import Password


@dto
class ChangePasswordRequest:
    id: UserId
    old_password: str | None  # None if the admin changes without the old one
    new_password: str


@dto
class ChangePasswordResponse:
    user: UserView


class ChangePassword(Interactor[ChangePasswordRequest, ChangePasswordResponse]):
    def __init__(
        self,
        user_repository: IUserRepository,
        user_reader: IUserReader,
        password_hasher: IPasswordHasher,
        transaction_manager: ITransactionManager,
        identity_provider: IIdentityProvider,
    ) -> None:
        self._user_repository: IUserRepository = user_repository
        self._user_reader: IUserReader = user_reader
        self._password_hasher: IPasswordHasher = password_hasher
        self._uow: ITransactionManager = transaction_manager
        self._idp: IIdentityProvider = identity_provider

    async def execute(self, request: ChangePasswordRequest) -> ChangePasswordResponse:
        current_user: User = await self._idp.get_user()
        self._check_access(current_user, request)

        user: User | None = await self._user_reader.find_by_id(request.id)
        if user is None:
            raise NotFoundError(f"User with id '{request.id}' not found")

        if request.old_password == request.new_password:
            raise ValidationError("New password cannot be the same as the old password")

        password = Password(value=request.new_password)
        password_hash: bytes = self._password_hasher.hash_password(password)

        user.password_hash = password_hash

        await self._user_repository.update(user)
        await self._uow.commit()

        return ChangePasswordResponse(user=UserView.from_domain(user))

    def _check_access(self, current_user: User, request: ChangePasswordRequest) -> None:
        is_self: bool = current_user.id == request.id
        is_admin: bool = current_user.role == UserRole.ADMINISTRATOR

        if not (is_self or is_admin):
            raise AccessDeniedError("You don't have permission to change another user's password")

        if is_admin:
            return

        if not request.old_password:
            raise AccessDeniedError("Old password is required")

        if not self._password_hasher.verify_password(
            request.old_password, current_user.password_hash
        ):
            raise AccessDeniedError("Old password is incorrect")

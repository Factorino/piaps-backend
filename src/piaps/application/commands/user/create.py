from uuid import uuid4

from piaps.application.common.dto.base import dto
from piaps.application.common.dto.user import UserDTO
from piaps.application.errors.auth import AccessDeniedError
from piaps.application.interfaces.auth.identity_provider import IIdentityProvider
from piaps.application.interfaces.auth.password_hasher import IPasswordHasher
from piaps.application.interfaces.common.interactor import Interactor
from piaps.application.interfaces.common.transaction_manager import ITransactionManager
from piaps.application.interfaces.readers.user import IUserReader
from piaps.application.interfaces.repositories.user import IUserRepository
from piaps.domain.entities.employee import EmployeeId
from piaps.domain.entities.user import User, UserId
from piaps.domain.enums.user_role import UserRole
from piaps.domain.errors.base import AlreadyExistsError
from piaps.domain.value_objects.password import Password
from piaps.domain.value_objects.username import Username


@dto
class CreateUserRequest:
    username: str
    password: str
    role: UserRole
    employee_id: EmployeeId | None = None


@dto
class CreateUserResponse:
    user: UserDTO


class CreateUser(Interactor[CreateUserRequest, CreateUserResponse]):
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

    async def execute(self, request: CreateUserRequest) -> CreateUserResponse:
        current_user: User = await self._idp.get_user()
        self._check_access(current_user)

        id_: UserId = UserId(uuid4())
        username = Username(value=request.username)
        password = Password(value=request.password)
        role: UserRole = request.role
        employee_id: EmployeeId | None = request.employee_id

        password_hash: bytes = self._password_hasher.hash_password(password)

        user = User(
            id=id_,
            username=username,
            password_hash=password_hash,
            role=role,
            employee_id=employee_id,
        )

        await self._check_unique(user)
        await self._user_repository.add(user)
        await self._uow.commit()

        return CreateUserResponse(user=UserDTO.from_domain(user))

    async def _check_unique(self, user: User) -> None:
        existing: User | None = await self._user_reader.find_by_username(user.username)
        if existing is not None and existing.id != user.id:
            raise AlreadyExistsError(f"User with username '{user.username.value}' already exists")

    def _check_access(self, current_user: User) -> None:
        if current_user.role < UserRole.ADMINISTRATOR:
            raise AccessDeniedError("You don't have permission to create users")

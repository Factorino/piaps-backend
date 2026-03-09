from uuid import uuid4

from piaps.application.common.dto.base import dto
from piaps.application.common.dto.user import UserDTO
from piaps.application.interfaces.auth.password_hasher import IPasswordHasher
from piaps.application.interfaces.common.interactor import Interactor
from piaps.application.interfaces.common.transaction_manager import ITransactionManager
from piaps.application.interfaces.readers.user import IUserReader
from piaps.application.interfaces.repositories.user import IUserRepository
from piaps.domain.entities.user import User, UserId
from piaps.domain.errors.base import AlreadyExistsError
from piaps.domain.value_objects.password import Password
from piaps.domain.value_objects.username import Username


@dto
class RegisterUserRequest:
    username: str
    password: str


@dto
class RegisterUserResponse:
    user: UserDTO


class RegisterUser(Interactor[RegisterUserRequest, RegisterUserResponse]):
    def __init__(
        self,
        user_repository: IUserRepository,
        user_reader: IUserReader,
        password_hasher: IPasswordHasher,
        transaction_manager: ITransactionManager,
    ) -> None:
        self._user_repository: IUserRepository = user_repository
        self._user_reader: IUserReader = user_reader
        self._password_hasher: IPasswordHasher = password_hasher
        self._uow: ITransactionManager = transaction_manager

    async def execute(self, request: RegisterUserRequest) -> RegisterUserResponse:
        id_: UserId = UserId(uuid4())
        username = Username(value=request.username)
        password = Password(value=request.password)

        password_hash: bytes = self._password_hasher.hash_password(password)

        user = User(
            id=id_,
            username=username,
            password_hash=password_hash,
        )

        await self._check_unique(user)
        await self._user_repository.add(user)
        await self._uow.commit()

        return RegisterUserResponse(user=UserDTO.from_domain(user))

    async def _check_unique(self, user: User) -> None:
        existing: User | None = await self._user_reader.find_by_username(user.username)
        if existing is not None and user.id != existing.id:
            raise AlreadyExistsError(f"User with username '{user.username.value}' already exists")

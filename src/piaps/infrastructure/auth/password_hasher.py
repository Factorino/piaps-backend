import bcrypt

from piaps.application.interfaces.auth.password_hasher import IPasswordHasher
from piaps.domain.value_objects.password import Password


class BcryptPasswordHasher(IPasswordHasher):
    def hash_password(self, password: Password) -> bytes:
        salt: bytes = bcrypt.gensalt()
        return bcrypt.hashpw(password.value.encode(), salt)

    def verify_password(self, raw: str, hashed: bytes) -> bool:
        if not raw or not hashed:
            return False

        try:
            return bcrypt.checkpw(raw.encode(), hashed)
        except (ValueError, TypeError):
            return False

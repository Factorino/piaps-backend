from piaps.application.errors.base import ApplicationError


class AuthenticationError(ApplicationError):
    pass


class InvalidCredentialsError(AuthenticationError):
    pass


class InvalidTokenError(AuthenticationError):
    pass


class TokenExpiredError(AuthenticationError):
    pass


class AccessDeniedError(ApplicationError):
    pass

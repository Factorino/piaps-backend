class AppError(Exception):
    pass


class DomainError(AppError):
    pass


class ValidationError(DomainError, ValueError, TypeError):
    pass


class AlreadyExistsError(DomainError):
    pass

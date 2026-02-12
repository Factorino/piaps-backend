from piaps.domain.errors.base import AppError


class ApplicationError(AppError):
    pass


class NotFoundError(ApplicationError):
    pass


class OperationFailedError(ApplicationError):
    pass

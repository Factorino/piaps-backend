from piaps.domain.errors.base import AppError


class ApplicationError(AppError):
    pass


class OperationFailedError(ApplicationError):
    pass


class DataMapperError(OperationFailedError):
    pass


class UnexpectedError(ApplicationError):
    pass

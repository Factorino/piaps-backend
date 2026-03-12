from types import MappingProxyType
from typing import Any, Final

from fastapi import Request, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from piaps.application.errors.auth import (
    AccessDeniedError,
    AuthenticationError,
)
from piaps.application.errors.base import (
    DataMapperError,
    OperationFailedError,
    UnexpectedError,
)
from piaps.domain.errors.base import (
    AlreadyExistsError,
    AppError,
    NotFoundError,
    ValidationError,
)
from piaps.domain.errors.payroll import (
    InvalidCalculationTypeError,
    InvalidPayrollRecordError,
    InvalidPayrollStatusError,
    PayrollValueNotSetError,
)


_ERROR_STATUS_CODE: Final[MappingProxyType[type[AppError], int]] = MappingProxyType(
    {
        # Domain errors
        ValidationError: status.HTTP_400_BAD_REQUEST,
        InvalidPayrollStatusError: status.HTTP_400_BAD_REQUEST,
        InvalidCalculationTypeError: status.HTTP_400_BAD_REQUEST,
        InvalidPayrollRecordError: status.HTTP_400_BAD_REQUEST,
        PayrollValueNotSetError: status.HTTP_400_BAD_REQUEST,
        AlreadyExistsError: status.HTTP_409_CONFLICT,
        NotFoundError: status.HTTP_404_NOT_FOUND,
        # Application errors
        AuthenticationError: status.HTTP_401_UNAUTHORIZED,
        AccessDeniedError: status.HTTP_403_FORBIDDEN,
        DataMapperError: status.HTTP_500_INTERNAL_SERVER_ERROR,
        OperationFailedError: status.HTTP_500_INTERNAL_SERVER_ERROR,
        # Fallback errors
        UnexpectedError: status.HTTP_500_INTERNAL_SERVER_ERROR,
        AppError: status.HTTP_500_INTERNAL_SERVER_ERROR,
    }
)


class ErrorResponse(BaseModel):
    status_code: int
    error_type: str
    message: str
    detail: dict[str, Any] = {}


def _get_error_status_code(exception: Exception) -> int:
    for cls in type(exception).mro():
        if cls in _ERROR_STATUS_CODE:
            return _ERROR_STATUS_CODE[cls]
    return status.HTTP_500_INTERNAL_SERVER_ERROR


def _get_error_type(exception: Exception) -> str:
    return type(exception).__qualname__


def _get_error_message(exception: Exception) -> str:
    return str(exception) if exception.args else f"{type(exception).__name__}: no message provided"


async def app_error_handler(_request: Request, exception: Exception) -> JSONResponse:
    error: AppError = exception if isinstance(exception, AppError) else UnexpectedError()
    error_status_code: int = _get_error_status_code(error)
    error_type: str = _get_error_type(error)
    error_message: str = _get_error_message(error)

    error_response: dict[str, Any] = ErrorResponse(
        status_code=error_status_code,
        error_type=error_type,
        message=error_message,
    ).model_dump(mode="json")

    return JSONResponse(
        status_code=error_status_code,
        content=error_response,
    )

from piaps.domain.errors.base import DomainError


class InvalidPayrollStatusError(DomainError):
    pass


class InvalidCalculationTypeError(DomainError):
    pass


class InvalidPayrollRecordError(DomainError):
    pass


class PayrollValueNotSetError(DomainError):
    pass

from enum import StrEnum


class PayrollStatus(StrEnum):
    DRAFT = "draft"
    CALCULATED = "CALCULATED"
    APPROVED = "approved"
    PAID = "PAID"

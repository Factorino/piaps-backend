from datetime import date
from decimal import Decimal

from piaps.application.common.dto.base import dto
from piaps.domain.enums.payroll_item_type import PayrollItemType


@dto
class PayrollRecordData:
    payroll_item_code: str
    payroll_item_name: str
    payroll_type: PayrollItemType
    amount: Decimal
    comment: str | None = None


@dto
class PayrollSheetData:
    period: date
    accruals_sum: Decimal
    deductions_sum: Decimal
    net_salary: Decimal
    records: list[PayrollRecordData]


@dto
class EmployeePayrollReportData:
    employee_code: str
    employee_full_name: str
    department_name: str
    position_name: str
    base_salary: Decimal
    sheets: list[PayrollSheetData]
    total_accruals: Decimal
    total_deductions: Decimal
    total_net_salary: Decimal

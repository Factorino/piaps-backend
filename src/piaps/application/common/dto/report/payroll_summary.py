from datetime import date
from decimal import Decimal

from piaps.application.common.dto.base import dto


@dto
class PayrollSummaryByDepartmentData:
    department_code: str
    department_name: str
    employee_count: int
    total_base_salary: Decimal
    total_accruals: Decimal
    total_deductions: Decimal
    total_net_salary: Decimal


@dto
class PayrollSummaryReportData:
    period_from: date | None
    period_to: date | None
    departments: list[PayrollSummaryByDepartmentData]
    total_employee_count: int
    grand_total_base_salary: Decimal
    grand_total_accruals: Decimal
    grand_total_deductions: Decimal
    grand_total_net_salary: Decimal

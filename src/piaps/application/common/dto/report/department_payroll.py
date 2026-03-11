from datetime import date
from decimal import Decimal

from piaps.application.common.dto.base import dto


@dto
class DepartmentEmployeePayrollData:
    employee_code: str
    employee_full_name: str
    position_name: str
    base_salary: Decimal
    accruals_sum: Decimal
    deductions_sum: Decimal
    net_salary: Decimal


@dto
class DepartmentPayrollReportData:
    department_code: str
    department_name: str
    period_from: date | None
    period_to: date | None
    employees: list[DepartmentEmployeePayrollData]
    total_base_salary: Decimal
    total_accruals: Decimal
    total_deductions: Decimal
    total_net_salary: Decimal
    employee_count: int
